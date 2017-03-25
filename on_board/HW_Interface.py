#! /usr/bin/python

#  Jeremy Lim
#  3/20/17
#  A python class used to set manage serial connections & issue commands
#  to the rover's arduino and servo controller for actuator control.

#  Dependencies: pyserial, numpy
import serial
import numpy as np
import math
#Used to standardize byte ordering.
import socket
#for implementing delays for serial initialization.
import time

# Exceptions used for this class:
from Rover_Exceptions import MessageError
from Rover_Exceptions import HardwareConnectError

class HW_Interface:

    def __init__(self):
        self.isOpen = False
        self.baudRate = 115200  # both controllers use the same baud rate
        self.arduinoFile = "/dev/ttyACM0"  # USB serial locations on the raspi.
        self.pololuFile  = "/dev/ttyACM1"  # to be updated later.

        # rover state
        self.right_motor = 0.0
        self.left_motor  = 0.0
        self.steer_angle = 0.0  # Let this be a float in degrees, where 0 is straight forward, 90 is perpendicular left,
                                # and -90 is perpendicular right.

        self.hopper_up = True     # true if our hopper is lifted.
        self.hopper_close = False # true if the hopper servos are closed.

        # Control constants
        self.hopper_up_micros    = 1500
        self.hopper_down_micros  = 1500

        self.hopper_open_micros  = 1500
        self.hopper_close_micros = 1500

        self.max_steer_angle = 30  # how far from 0 or steering angle can be (0+-max_steer_angle)

        self.max_motor_velocity = 1.0  # Constant for maximum allowed motor speed. cm/s. To be defined later.

        # servo angle mapping:
        # (duty cycle in microseconds)
        # 1500 is dead center
        # 2400 is at 90deg.
        # 600 is at -90deg.
        self.servo_mid = 1500
        self.servo_max = 2400
        self.servo_min = 600

        # Physical constants of the rover (length, width, etc.
        self.drive_wheel_width = 1.0#in cm
        self.chassis_wheel_length = 1.0#in cm

    # Open the serial connections with our peripherals.
    # Set up some state variables.
    def open_connections(self):
        self.arduino = serial.Serial(self.arduinoFile,self.baudRate)

        self.pololu =  serial.Serial(self.pololuFile,self.baudRate)
        #  wait for chip initialization
        time.sleep(0.5)
        #  start byte
        self.pololu.write(np.int8(0xAA))
        time.sleep(0.5)

        self.isOpen = True

    #  Gracefully end connections with the arduino and servo controller
    def close_connections(self):
        self.pololu.close()
        self.arduino.close()
        self.isOpen = False

    # Stop the movement of all actuators & motors on the rover.
    # takes the form of a special flag command to the arduino.
    def send_all_stop(self):
        self.left_motor  = 0.0
        self.right_motor = 0.0
        return self.send_arduino_command(True, self.left_motor, self.right_motor, False)

    # Designate the state of the rover to be sent to the low-level hardware.
    #  Float, Float, Bool, Bool
    def send_rover_command(self, in_steer_angle, in_velocity, in_hopper_grasp, in_hopper_up):

        if not self.isOpen:
            # throw an exception if we haven't opened our connections.
            raise HardwareConnectError("Message send to Arduino & Pololu; Serial comms not open.")

        #  update internal state
        if in_steer_angle > self.max_steer_angle:
            self.steer_angle = self.max_steer_angle    
        elif in_steer_angle < -self.max_steer_angle: 
            self.steer_angle = -self.max_steer_angle    
        else:
            self.steer_angle = in_steer_angle
        #  calculate motor velocities from the steering angle and our linear velocity.
        if self.steer_angle != 0:
            turnRadius = self.chassis_wheel_length*math.tan(math.pi/2.0 + self.steer_angle/180.0*math.pi)
            if self.steer_angle > 0.0:
                turnRadius = -self.chassis_wheel_length*math.tan(math.pi/2.0 + self.steer_angle/180.0*math.pi)
            elif self.steer_angle < 0.0:
                turnRadius = self.chassis_wheel_length*math.tan(math.pi/2.0 + self.steer_angle/180.0*math.pi)
            #  find the desired angular velocity
            omega = in_velocity/turnRadius
            #  See if this angular velocity is possible with our max wheel velocity.

            #  assign wheel velocities as needed.
            if in_velocity > 0.0:
                self.left_motor = omega*(abs(turnRadius)+self.drive_wheel_width/2.0)
                self.right_motor = omega*(abs(turnRadius)-self.drive_wheel_width/2.0)
            else:
                self.left_motor = -omega*(abs(turnRadius)+self.drive_wheel_width/2.0)
                self.right_motor = -omega*(abs(turnRadius)-self.drive_wheel_width/2.0)

        else:  #  straight forward/backward
            self.right_motor = 0.0
            self.left_motor  = 0.0

        self.hopper_up = in_hopper_up
        self.hopper_grasp = in_hopper_grasp

        # send commands over serial
        return self.send_pololu_command(in_steer_angle, self.hopper_up, self.hopper_grasp) and self.send_arduino_command(False, self.left_motor, self.right_motor, False)

    #  Check measured state of actuators & sensors
    #  this must be called repeatedly to get an accurate state of the rover.
    def check_sover_status(self):
        #  only check status if the connection is open.
        if self.isOpen:
            msg_buffer = []
            msg_buffer = self.arduino.read(37)#  read some bytes from the arduino. It's response is 37 bytes in length.
            if msg_buffer[0] == 0x32:#  first number is correct, then parse the message.
                msg_buffer = np.array(msg_buffer)#  convert into np array
                
                right_velocity = socket.ntohl(np.float32(msg_buffer[1:5]))
                left_velocity = socket.ntohl(np.float32(msg_buffer[4:9]))
                #  angleVelocity = socket.ntohl(np.float32(msgBuffer[8:13])) #unused
                x_position = socket.ntohl(np.float32(msg_buffer[12:17]))
                y_position = socket.ntohl(np.float32(msg_buffer[16:21]))
                heading = socket.ntohl(np.float32(msg_buffer[20:25]))     #unused
                battery_voltage = socket.ntohl(np.float32(msg_buffer[24:29]))
                ir_elevation = socket.ntohl(np.float32(msg_buffer[28:33]))
                ir_heading = socket.ntohl(np.float32(msg_buffer[32:37]))
                #  status_byte = msgBuffer[37]  #unused.
                is_Valid = True
            else:
                #  Might've gotten a message halfway. Throw error
                # Message Format EXCEPTION
                is_Valid = False
                raise MessageError("Arduino Magic Number Mismatch.")
        else:
            # Connectivity exception
            # batteryVoltage, xPosition, yPosition, heading, leftVelocity, rightVelocity, IR_heading, IR_elevation = 0.0
            is_Valid = False
            raise HardwareConnectError("Message request of Arduino; Serial comms not open.")

        #  Bool, float(volts), float(meters), float(meters), float(radians), float(cm/s), float(cm/s), float(degrees), float(degrees)
        return is_Valid, battery_voltage, x_position, y_position, heading, left_velocity, right_velocity, ir_heading, ir_elevation

    #  turn a value in microseconds into the pololu mini-maestro format
    def get_duty_cycle(self, in_microSecs):
        #  Multiply by 4: the maestro operates in quarter-microseconds.
        duty = 4*in_microSecs
        #  we send the
        low_bits = duty & 0x007F
        high_bits = (duty >> 7) & 0x7F
        #  list of np.int8s
        byte_list = [np.int8(low_bits),np.int8(high_bits)]
        return byte_list

    #  build the serial command to send to the servo controller.
    def send_pololu_command(self, in_steerServo, in_hopper_up, in_hopper_grasp):
        #  Check if connection is open.
        if self.isOpen:
            #  build our message
            command_bytes = []
            command_bytes.append(np.int8(0x9F))  # Command byte
            command_bytes.append(np.int8(4))     # Number of channels we're controlling
            command_bytes.append(np.int8(0))     # The start channel (the first one in this case)
            
            # Servo 0: Steering servo
            # Servo 1: Hopper lift servo
            # Servo 2: Hopper Claw servo 1
            # Servo 3: Hopper Claw servo 2
            steer_conversion = in_steerServo/90.0*(self.servo_max-self.servo_mid) + self.servo_mid

            # list composition.
            command_bytes += self.get_duty_cycle(steer_conversion)

            if in_hopper_up:  # true for lifted hopper
                command_bytes += self.get_duty_cycle(self.hopper_up_micros)
            else:
                command_bytes += self.get_duty_cycle(self.hopper_down_micros)

            if in_hopper_grasp:  # true for closed grasper
                command_bytes += self.get_duty_cycle(self.hopper_close_micros)  # these duty cycles will need adjustment.
                command_bytes += self.get_duty_cycle(self.hopper_close_micros)  # these duty cycles will need adjustment.
            else:
                command_bytes += self.get_duty_cycle(self.hopper_open_micros)   # these duty cycles will need adjustment.
                command_bytes += self.get_duty_cycle(self.hopper_open_micros)   # these duty cycles will need adjustment.

            write_bytes = bytearray(np.array(command_bytes))
            self.pololu.write(write_bytes)

            return True  # True for success
        else:
            # Non-open exception
            raise HardwareConnectError("Message send to Pololu; Serial comms not open.")
            # Can't send any commands.

    # build the serial command to send to the arduino.
    def send_arduino_command(self, in_stop_flag, in_left_mot, in_right_mot, in_reset_odometry_flag):
        if self.isOpen:
            command_bytes = []
            command_bytes.append(np.int8(0x32))   # magic number
            if in_stop_flag:
                command_bytes.append(np.int8(0x2))  # E-stop command.
            elif in_reset_odometry_flag:
                command_bytes.append(np.int8(0x1))  # Signal to reset odometry.
            else:
                leftFloat = socket.htonl(np.float32(in_left_mot))   # using network byte order for transmission; keep consistency.
                rightFloat = socket.htonl(np.float32(in_right_mot))
                command_bytes.append(np.int8(0x0))                  # Signal for motor control.
                command_bytes.append(rightFloat)
                command_bytes.append(leftFloat)

            write_bytes = bytearray(np.array(command_bytes))
            self.arduino.write(write_bytes)
            return True
        else:
            # Raise non-open exception
            raise HardwareConnectError("Message send to Arduino; Serial comms not open.")
            # Can't send any commands.
