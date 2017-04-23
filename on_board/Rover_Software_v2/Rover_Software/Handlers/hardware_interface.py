#! /usr/bin/python

#  Jeremy Lim
#  4/19/17
#  A python class used to set manage serial connections & issue commands
#  to the rover's arduino and servo controller for actuator control.

#  Dependencies: pyserial, numpy
import math
import numpy as np
import serial
# Used to standardize byte ordering.
import socket
import struct
# for implementing delays for serial initialization.
import time
# Exceptions used for this class:
from Rover_Classes.rover_exceptions import HardwareConnectError
from Rover_Classes.rover_exceptions import MessageError


class HardwareInterface:
    def __init__(self):
        self.is_open = False
        self.baudRate = 115200  # both controllers use the same baud rate
        self.arduino_file = "/dev/ttyUSB0"  # USB serial locations on the raspi.
        self.pololu_file = "/dev/ttyACM0"  # to be updated later.

        # rover state
        self.right_motor = 0.0
        self.left_motor = 0.0
        self.steer_angle = 0.0  # Let this be a float in degrees, where 0 is straight forward, 90 is perpendicular left,
        # and -90 is perpendicular right.

        self.hopper_up = True  # true if our hopper is lifted.
        self.hopper_close = False  # true if the hopper servos are closed.

        # Control constants
        self.hopper_up_micros = 1500
        self.hopper_down_micros = 1500

        self.hopper_open_right_micros = 600 
        self.hopper_open_left_micros = 2400
        self.hopper_close_micros = 1500

        self.max_steer_angle = 60.0  # how far from 0 or steering angle can be (0+-max_steer_angle).

        self.max_motor_velocity = 10.0  # Constant for maximum allowed motor speed. cm/s. To be defined later.

        # servo angle mapping:
        # (duty cycle in microseconds)
        # 1500 is dead center
        # 2400 is at 90deg.
        # 600 is at -90deg.
        self.servo_mid = 1500
        self.servo_max = 2400
        self.servo_min = 600

        # Physical constants of the rover (length, width, etc.
        self.drive_wheel_width = 43.0  # in cm
        self.chassis_wheel_length = 34.0  # in cm

        # Initiates attributes for later use
        self.arduino = None
        self.pololu = None

        #  turn a value in microseconds into the pololu mini-maestro format

    def get_duty_cycle(self, in_micro_secs):
        #  Multiply by 4: the maestro operates in quarter-microseconds.
        duty = long(4 * in_micro_secs)
        #  we send the
        low_bits = duty & 0x007F
        high_bits = (duty >> 7) & 0x7F
        #  list of np.int8s
        byte_list = [np.int8(low_bits), np.int8(high_bits)]
        return byte_list

        #  build the serial command to send to the servo controller.

    def send_pololu_command(self, in_steer_servo, in_hopper_up, in_hopper_grasp):
        #  Check if connection is open.
        if self.is_open:
            #  build our message
            command_bytes = []
            command_bytes.append(np.int8(0x9F))  # Command byte
            command_bytes.append(np.int8(4))  # Number of channels we're controlling
            command_bytes.append(np.int8(0))  # The start channel (the first one in this case)

            # Servo 0: Steering servo 1 # Right steering
            # Servo 1: Steering servo 2 # Left steering
            # Servo 2: Hopper lift servo 1 #right servo
            # Servo 3: Hopper lift servo 2 # left servo
            # Servo 4: Hopper Claw servo 1 # Right claw
            # Servo 5: Hopper Claw servo 2 # Left claw
            steer_conversion = in_steer_servo / 90.0 * (self.servo_max - self.servo_mid) + self.servo_mid

            # list composition.
            command_bytes = [np.int8(0x84), np.int8(0)]
            command_bytes += self.get_duty_cycle(steer_conversion)
            self.pololu.write(bytearray(np.array(command_bytes)))# Servo 0

            command_bytes = [np.int8(0x84), np.int8(1)]
            command_bytes += self.get_duty_cycle(steer_conversion)
            self.pololu.write(bytearray(np.array(command_bytes)))  # Servo 1

            hopper_cmd = []

            if in_hopper_up:  # true for lifted hopper
                hopper_cmd = self.get_duty_cycle(self.hopper_up_micros)
            else:
                hopper_cmd = self.get_duty_cycle(self.hopper_down_micros)

            command_bytes = [np.int8(0x84), np.int8(2)]
            command_bytes += hopper_cmd
            self.pololu.write(bytearray(np.array(command_bytes)))  # Servo 2

            command_bytes = [np.int8(0x84), np.int8(3)]
            command_bytes += hopper_cmd
            self.pololu.write(bytearray(np.array(command_bytes)))  # Servo 3

            if in_hopper_grasp:  # true for closed grasper
                claw_cmd = self.get_duty_cycle(
                    self.hopper_close_micros)  

                command_bytes = [np.int8(0x84), np.int8(4)]
                command_bytes += claw_cmd
                self.pololu.write(bytearray(np.array(command_bytes)))  # Servo 4

                command_bytes = [np.int8(0x84), np.int8(5)]
                command_bytes += claw_cmd
                self.pololu.write(bytearray(np.array(command_bytes)))  # Servo 5

            else:                #Open grasper

                command_bytes = [np.int8(0x84), np.int8(4)]
                command_bytes += self.get_duty_cycle(
                    self.hopper_open_right_micros)
                self.pololu.write(bytearray(np.array(command_bytes)))  # Servo 4

                command_bytes = [np.int8(0x84), np.int8(5)]
                command_bytes += self.get_duty_cycle(
                    self.hopper_open_left_micros)
                self.pololu.write(bytearray(np.array(command_bytes)))  # Servo 5

        else:
            # Non-open exception
            raise HardwareConnectError("Message send to Pololu; Serial comms not open.")
            # Can't send any commands.

            # build the serial command to send to the arduino.

    def send_arduino_command(self, in_stop_flag, in_left_mot, in_right_mot, in_reset_odometry_flag):
        if self.is_open:
            #Specifying network byte order.
            #command_bytes = []
            #command_bytes.append(np.int8(0x32))  # magic number
            if in_stop_flag:
                command_bytes = struct.pack('!bb', 0x32, 0x2)
                #command_bytes.append(np.int8(0x2))  # E-stop command.
            elif in_reset_odometry_flag:
                command_bytes = struct.pack('!bb', 0x32, 0x1)
                #command_bytes.append(np.int8(0x1))  # Signal to reset odometry.
            else:
                command_bytes = struct.pack('!bbff', 0x32, 0x0, in_left_mot, in_right_mot)
                #left_float = socket.htonl(
                    #np.float32(in_left_mot))  # using network byte order for transmission; keep consistency.
                #right_float = socket.htonl(np.float32(in_right_mot))
                #command_bytes.append(np.int8(0x0))  # Signal for motor control.
                #command_bytes.append(right_float)
                #command_bytes.append(left_float)

            write_bytes = bytearray(command_bytes)
            self.arduino.write(write_bytes)
        else:
            # Raise non-open exception
            raise HardwareConnectError("Message send to Arduino; Serial comms not open.")
            # Can't send any commands.

    # Open the serial connections with our peripherals.
    # Set up some state variables.
    def open_connections(self):
        self.arduino = serial.Serial(self.arduino_file, self.baudRate)

        self.pololu = serial.Serial(self.pololu_file, self.baudRate)
        #  wait for chip initialization
        time.sleep(0.5)
        #  start byte
        self.pololu.write(np.array_str(np.array(np.int8(0xAA))))
        time.sleep(0.5)

        self.is_open = True
        print("++ Rover connection successful")

    #  Gracefully end connections with the arduino and servo controller
    def close_connections(self):
        self.pololu.close()
        self.arduino.close()
        self.is_open = False
        print("++ Rover connection closed")

    # Stop the movement of all actuators & motors on the rover.
    # takes the form of a special flag command to the arduino.
    # For emergency stop.
    def send_emergency_stop(self):
        self.left_motor = 0.0
        self.right_motor = 0.0
        self.send_arduino_command(True, self.left_motor, self.right_motor, False)
        print("++ Emergency stop activated")

    # Stop the movement of all actuators & motors on the rover.
    # Reset the hopper to the up position.
    # for regular reset (not emergencies!)
    def send_stop(self):
        self.left_motor = 0.0
        self.right_motor = 0.0
        # Do not send the e-stop flag.
        self.send_arduino_command(False, self.left_motor, self.right_motor, False)
        # reset hopper to the up and closed position.
        # steering is reset to straight ahead.
        self.send_pololu_command(0.0, True, True)
        print("++ Rover stopped")

    # Designate the state of the rover to be sent to the low-level hardware.
    #  Float, Float, Bool, Bool
    def send_rover_command(self, in_steer_angle, in_velocity, in_hopper_grasp, in_hopper_up):

        if not self.is_open:
            # throw an exception if we haven't opened our connections.
            raise HardwareConnectError("Message send to Arduino & Pololu; Serial comms not open.")

        motor_vel = in_velocity
        if in_velocity > self.max_motor_velocity:
            motor_vel = self.max_motor_velocity
        elif in_velocity < -self.max_motor_velocity:
            motor_vel = -self.max_motor_velocity

        # update internal state
        if in_steer_angle > self.max_steer_angle:
            self.steer_angle = self.max_steer_angle
        elif in_steer_angle < -self.max_steer_angle:
            self.steer_angle = -self.max_steer_angle
        else:
            self.steer_angle = in_steer_angle
        # calculate motor velocities from the steering angle and our linear velocity.
        if self.steer_angle != 0:
            #turn_radius = self.chassis_wheel_length * math.tan(math.pi / 2.0 + self.steer_angle / 180.0 * math.pi)
            #if self.steer_angle > 0.0:
                #turn_radius = -self.chassis_wheel_length * math.tan(self.steer_angle / 180.0 * math.pi)
            #elif self.steer_angle < 0.0:
            turn_radius = self.chassis_wheel_length * math.tan((math.pi/2.0) + abs(self.steer_angle / 180.0 * math.pi))
            # find the desired angular velocity
            omega = motor_vel / -turn_radius
            #  See if this angular velocity is possible with our max wheel velocity.

            #  assign wheel velocities as needed.
            if motor_vel > 0.0:
		if omega > 0.0:
               	    self.left_motor = omega * (abs(turn_radius) - self.drive_wheel_width / 2.0)
                    self.right_motor = omega * (abs(turn_radius) + self.drive_wheel_width / 2.0)
                else:
               	    self.left_motor = -omega * (abs(turn_radius) + self.drive_wheel_width / 2.0)
                    self.right_motor = -omega * (abs(turn_radius) - self.drive_wheel_width / 2.0)
            else:
                if omega > 0.0:
                    self.left_motor = -omega * (abs(turn_radius) - self.drive_wheel_width / 2.0)
                    self.right_motor = -omega * (abs(turn_radius) + self.drive_wheel_width / 2.0)
                else:
                    self.left_motor = omega * (abs(turn_radius) + self.drive_wheel_width / 2.0)
                    self.right_motor = omega * (abs(turn_radius) - self.drive_wheel_width / 2.0)
                    

        else:  # straight forward/backward
            self.right_motor = motor_vel
            self.left_motor = motor_vel

        self.hopper_up = in_hopper_up
        self.hopper_close = in_hopper_grasp

        # send commands over serial
        self.send_pololu_command(in_steer_angle, self.hopper_up, self.hopper_close)
        self.send_arduino_command(False, self.left_motor, self.right_motor, False)
        print("++++++++++++++++++++++++++++")
        print("++ Command sent")
        print("++++++++++++++++++++++++++++")
        print("++ Angle: " + str(in_steer_angle))
        print("++ Left Motor: " + str(self.left_motor))
        print("++ Right Motor: " + str(self.right_motor))
        print("++ Hopper Up: " + str(self.hopper_up))
        print("++ Hopper Closed: " + str(self.hopper_close))
        print("++++++++++++++++++++++++++++")

    #  Check measured state of actuators & sensors
    #  this must be called repeatedly to get an accurate state of the rover.
    def check_rover_status(self):
        #  only check status if the connection is open.
        if self.is_open:
            msg_buffer = self.arduino.read(
                38)  # read some bytes from the arduino. It's response is 37 bytes in length.
            if msg_buffer[0] == 0x32:  # first number is correct, then parse the message.
                msg_buffer = np.array(msg_buffer)  # convert into np array

                right_velocity = socket.ntohl(np.float32(msg_buffer[1:5]))
                left_velocity = socket.ntohl(np.float32(msg_buffer[4:9]))
                #  angleVelocity = socket.ntohl(np.float32(msgBuffer[8:13])) #unused
                x_position = socket.ntohl(np.float32(msg_buffer[12:17]))
                y_position = socket.ntohl(np.float32(msg_buffer[16:21]))
                heading = socket.ntohl(np.float32(msg_buffer[20:25]))  # unused
                battery_voltage = socket.ntohl(np.float32(msg_buffer[24:29]))
                ir_elevation = socket.ntohl(np.float32(msg_buffer[28:33]))
                ir_heading = socket.ntohl(np.float32(msg_buffer[32:37]))
                #  status_byte = msgBuffer[37]  #unused.
                is_valid = True

                print("++++++++++++++++++++++++++++")
                print("++ Rover Status")
                print("++++++++++++++++++++++++++++")
                print("++ X Pos: " + str(x_position))
                print("++ Y Pos: " + str(y_position))
                print("++ Heading: " + str(heading))
                print("++ Left Velocity: " + str(left_velocity))
                print("++ Right Velocity: " + str(right_velocity))
                print("++ IR Heading: " + str(ir_heading))
                print("++ IR Elevation: " + str(ir_elevation))
                print("++++++++++++++++++++++++++++")

                # Bool,
                # float(volts),
                # float(meters),
                # float(meters),
                # float(radians),
                # float(cm/s),
                # float(cm/s),
                # float(degrees),
                # float(degrees)
                return is_valid, \
                       battery_voltage, \
                       x_position, \
                       y_position, \
                       heading, \
                       left_velocity, \
                       right_velocity, \
                       ir_heading, \
                       ir_elevation

            else:
                #  Might've gotten a message halfway. Throw error
                # Message Format EXCEPTION
                # is_valid = False
                raise MessageError("Arduino Magic Number Mismatch.")
        else:
            # Connectivity exception
            # batteryVoltage, xPosition, yPosition, heading, leftVelocity, rightVelocity, IR_heading, IR_elevation = 0.0
            # is_valid = False
            raise HardwareConnectError("Message request of Arduino; Serial comms not open.")
