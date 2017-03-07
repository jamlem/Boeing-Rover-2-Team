#! /usr/bin/python

#Jeremy Lim
#3/7/17
#A python class used to set manage serial connections & issue commands
#to the rover's arduino and servo controller for actuator control.

#Dependencies: pyserial, numpy
import serial
import numpy as np
import math
#Used to standardize byte ordering.
import socket
#for implementing delays for serial initialization.
import time

class HW_Interface:

    def __init__(self):
        self.isOpen = False
        self.baudRate = 115200#both controllers use the same baud rate
        self.arduinoFile = "/dev/ttyACM0"#USB serial locations on the raspi.
        self.pololuFile =  "/dev/ttyACM1"#to be updated later.

        #rover state
        self.right_motor = 0.0
        self.left_motor  = 0.0
        self.steer_angle = 0.0#Let this be a float in degrees, where 0 is straight forward, 90 is perpendicular left,
                              #and -90 is perpendicular right.

        self.hopper_up = True#true if our hopper is lifted.
        self.hopper_close = False#true if the hopper servos are closed.

        #Control constants
        self.hopper_up_micros    = 1500
        self.hopper_down_micros  = 1500

        self.hopper_open_micros  = 1500
        self.hopper_close_micros = 1500

        self.max_steer_angle = 30 #how far from 0 or steering angle can be (0+-max_steer_angle)

        self.max_motor_velocity = 1.0 #Constant for maximum allowed motor speed. cm/s. To be defined later.

        #servo angle mapping:
        #(duty cycle in microseconds)
        #1500 is dead center
        #2400 is at 90deg.
        #600 is at -90deg.
        self.servo_mid = 1500
        self.servo_max = 2400
        self.servo_min = 600

        #Physical constants of the rover (length, width, etc.
        self.drive_wheel_width = 1.0#in cm
        self.chassis_wheel_length = 1.0#in cm

    #Open the serial connections with our peripherals.
    #Set up some state variables.
    def openConnections(self):
        self.arduino = serial.Serial(self.arduinoFile,self.baudRate)

        self.pololu = serial.Serial(self.pololuFile,self.baudRate)
        #wait for chip initialization
        time.sleep(0.5)
        #start byte
        self.pololu.write(np.int8(0xAA))
        time.sleep(0.5)

        self.isOpen = True

    #Gracefully end connections with the arduino and servo controller
    def closeConnections(self):
        self.pololu.close()
        self.arduino.close()
        self.isOpen = False

    #Stop the movement of all actuators & motors on the rover.
    #takes the form of a special flag command to the arduino.
    def sendAllStop(self):
        self.left_motor = 0.0
        self.right_motor = 0.0
        return sendArduinoCommand(True,self.left_motor,self.right_motor,False)

    #Designate the state of the rover to be sent to the low-level hardware.
    #Float, Float, Bool, Bool
    def sendRoverCommand(self,in_steer_angle,in_velocity,in_hopper_grasp,in_hopper_up):
        #update internal state
        if in_steer_angle > self.max_steer_angle:
            self.steer_angle = self.max_steer_angle    
        elif in_steer_angle < -self.max_steer_angle: 
            self.steer_angle = -self.max_steer_angle    
        else:
            self.steer_angle = in_steer_angle
        #calculate motor velocities from the steering angle and our linear velocity.
        if self.steer_angle != 0:
            turnRadius = self.chassis_wheel_length*tan(math.pi/2.0 + self.steer_angle/180.0*math.pi)
            if self.steer_angle > 0.0:
                turnRadius = -self.chassis_wheel_length*tan(math.pi/2.0 + self.steer_angle/180.0*math.pi)
            else self.steer_angle < 0.0:
                turnRadius = self.chassis_wheel_length*tan(math.pi/2.0 + self.steer_angle/180.0*math.pi)
            #find the desired angular velocity
            omega = in_velocity/turnRadius
            #See if this angular velocity is possible with our max wheel velocity.

            #assign wheel velocities as needed.
            if in_velocity > 0.0:
                self.left_motor = omega*(abs(turnRadius)+self.drive_wheel_width/2.0)
                self.right_motor = omega*(abs(turnRadius)-self.drive_wheel_width/2.0)
            else:
                self.left_motor = -omega*(abs(turnRadius)+self.drive_wheel_width/2.0)
                self.right_motor = -omega*(abs(turnRadius)-self.drive_wheel_width/2.0)

        else:#straight forward/backward
            self.right_motor = 0.0
            self.left_motor  = 0.0

        self.hopper_up = in_hopper_up
        self.hopper_grasp = in_hopper_close

        #send commands over serial
        return sendPololuCommand(in_steerServo,self.hopper_up,self.hopper_grasp) and sendArduinoCommand(False,self.left_motor,self.right_motor,False)
            
    #Check measured state of actuators & sensors
    #this must be called repeatedly to get an accurate state of the rover.
    def checkRoverStatus(self):
        #only check status if the connection is open.
        if self.isOpen:
            msgbuffer = []
            msgbuffer = self.arduino.read(37)#read some bytes from the arduino. It's response is 37 bytes in length.
            if msgbuffer[0] == 0x32:#first number is correct, then parse the message.
                msgbuffer = np.array(msgbuffer)#convert into np array
                
                rightVelocity = socket.ntohl(np.float32(msgBuffer[1:5]))
                leftVelocity = socket.ntohl(np.float32(msgBuffer[4:9]))
                #angleVelocity = socket.ntohl(np.float32(msgBuffer[8:13])) #unused
                xPosition = socket.ntohl(np.float32(msgBuffer[12:17]))
                yPosition = socket.ntohl(np.float32(msgBuffer[16:21]))
                heading = socket.ntohl(np.float32(msgBuffer[20:25]))     #unused
                batteryVoltage = socket.ntohl(np.float32(msgBuffer[24:29]))
                IR_elevation = socket.ntohl(np.float32(msgBuffer[28:33]))
                IR_heading = socket.ntohl(np.float32(msgBuffer[32:37]))
                #status_byte = msgBuffer[37]  #unused.
                is_Valid = True
            else:
                #Might've gotten a message halfway. Throuw
                is_Valid = False
        else
            batteryVoltage, xPosition, yPosition, heading, leftVelocity, rightVelocity, IR_heading, IR_elevation = 0.0
            is_Valid = False

        #Bool, float(volts), float(meters), float(meters), float(radians), float(cm/s), float(cm/s), float(degrees), float(degrees)
        return is_Valid, batteryVoltage, xPosition, yPosition, heading, leftVelocity, rightVelocity, IR_heading, IR_elevation

    #Check system state for errors
    def pollHealthStatus(self):
        #TODO: define error states for this class!
        #undefined for now.
    #HELPER METHODS--------------------------------

    #turn a value in microseconds into the pololu mini-maestro format
    def getDutyCycle(self,in_microSecs):
        #Multiply by 4: the maestro operates in quarter-microseconds.
        duty = 4*in_microSecs
        #we send the 
        lowBits = duty & 0x007F
        highBits = (duty >> 7) & 0x7F
        #list of np.int8s
        byteList = [np.int8(lowBits),np.int8(highBits)]
        return byteList

    #build the serial command to send to the servo controller.
    def sendPololuCommand(self,in_steerServo,in_hopper_up,in_claw_closed):
        #Check if connection is open.
        if self.isOpen:
            #build our message
            commandBytes = []
            commandBytes.append(np.int8(0x9F)) #Command byte
            commandBytes.append(np.int8(4)) #Number of channels we're controlling
            commandBytes.append(np.int8(0)) #The start channel (the first one in this case)
            
            #Servo 0: Steering servo
            #Servo 1: Hopper lift servo
            #Servo 2: Hopper Claw servo 1
            #Servo 3: Hopper Claw servo 2
            steer_conversion = in_steerServo/90.0*(self.servo_max-self.servo_mid) + self.servo_mid

            commandBytes.append(getDutyCycle(steer_conversion))

            if in_hopper_up:#true for lifted hopper
                commandBytes.append(getDutyCycle(self.hopper_up_micros))
            else:
                commandBytes.append(getDutyCycle(self.hopper_down_micros))

            if in_hopper_grasp:#true for closed grasper
                commandBytes.append(getDutyCycle(self.hopper_close_micros))#these duty cycles will need adjustment.
                commandBytes.append(getDutyCycle(self.hopper_close_micros))#these duty cycles will need adjustment.
            else:
                commandBytes.append(getDutyCycle(self.hopper_open_micros))#these duty cycles will need adjustment.
                commandBytes.append(getDutyCycle(self.hopper_open_micros))#these duty cycles will need adjustment.

            self.pololu.write(commandBytes)

            return True#True for success
        else:
            return False#Can't send any commands.

    #build the serial command to send to the arduino.
    def sendArduinoCommand(self,in_stop_flag,in_left_mot,in_right_mot,in_reset_odometry_flag):
        if self.isOpen:
            commandBytes = []
            commandBytes.append(np.int8(0x32))#magic number
            if in_stop_flag:
                commandBytes.append(np.int8(0x2))#E-stop command.
                self.arduino.write(commandBytes)
            elif in_reset_odometry_flag:
                commandBytes.append(np.int8(0x1))#Signal to reset odometry.
                self.arduino.write(commandBytes)
            else:
                leftFloat = socket.htonl(np.float32(in_left_mot))#using network byte order for transmission; keep consistency.
                rightFloat = socket.htonl(np.float32(in_right_mot))
                commandBytes.append(np.int8(0x0))#Signal for motor control.
                commandBytes.append(rightFloat)
                commandBytes.append(leftFloat)
                self.arduino.write(commandBytes)
            return True
        else
            return False
