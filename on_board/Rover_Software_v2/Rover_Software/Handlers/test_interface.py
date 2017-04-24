#! /usr/bin/python

#  Jeremy Lim
#  4/19/17
#  A python class used to set manage serial connections & issue commands
#  to the rover's arduino and servo controller for actuator control.

# EDITED FOR TESTING PURPOUSES
# USE TO TEST CONNECTION WIHTOUT ARDUINO INTERGATION
#  Dependencies: pyserial, numpy
import math
from Rover_Classes.rover_exceptions import HardwareConnectError


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
        #  build the serial command to send to the servo controller.

    # Open the serial connections with our peripherals.
    # Set up some state variables.
    def open_connections(self):
        self.is_open = True
        print("++ Rover connection successful")

    #  Gracefully end connections with the arduino and servo controller
    def close_connections(self):
        self.is_open = False
        print("++ Rover connection closed")

    # Stop the movement of all actuators & motors on the rover.
    # takes the form of a special flag command to the arduino.
    # For emergency stop.
    def send_emergency_stop(self):
        print("++ Emergency stop activated")

    # Stop the movement of all actuators & motors on the rover.
    # Reset the hopper to the up position.
    # for regular reset (not emergencies!)
    def send_stop(self):
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
            # turn_radius = self.chassis_wheel_length * math.tan(math.pi / 2.0 + self.steer_angle / 180.0 * math.pi)
            # if self.steer_angle > 0.0:
                # turn_radius = -self.chassis_wheel_length * math.tan(self.steer_angle / 180.0 * math.pi)
            # elif self.steer_angle < 0.0:
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
        import random
        if self.is_open:

            right_velocity = random.randrange(0, 100)/100
            left_velocity = random.randrange(0, 100) / 100
            #  angleVelocity = socket.ntohl(np.float32(msgBuffer[8:13])) #unused
            x_position = random.randrange(0, 100)
            y_position = random.randrange(0, 100)
            heading = random.randrange(0, 100)/100*360  # unused
            battery_voltage = random.randrange(0, 100)
            ir_elevation = random.randrange(0, 100)
            ir_heading = random.randrange(0, 100)/100*360
            #  status_byte = msgBuffer[37]  #unused.
            is_valid = True

            print("++++++++++++++++++++++++++++")
            print("++ Rover Status")
            print("++++++++++++++++++++++++++++")
            print("++ Is Valid: " + str(is_valid))
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
            # Connectivity exception
            # batteryVoltage, xPosition, yPosition, heading, leftVelocity, rightVelocity, IR_heading, IR_elevation = 0.0
            # is_valid = False
            raise HardwareConnectError("Message request of Arduino; Serial comms not open.")
