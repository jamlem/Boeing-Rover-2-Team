import random

'''
A test class to ensure the correct values are passing to and from the class.
The naming, parameters, and returns from the PSU library will be used

Only the methods that will be needed to test logic will be copied
'''


class HWInterfaceTest:
    def __init__(self):
        self.isOpen = False
        self.baudRate = 115200  # both controllers use the same baud rate
        self.arduinoFile = "/dev/ttyACM0"  # USB serial locations on the raspi.
        self.pololuFile = "/dev/ttyACM1"  # to be updated later.

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

        self.hopper_open_micros = 1500
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
        self.drive_wheel_width = 1.0  # in cm
        self.chassis_wheel_length = 1.0  # in cm

    def open_connections(self):
        self.isOpen = True
        print("Connection Open")

        # Gracefully end connections with the arduino and servo controller

    def close_connections(self):
        self.isOpen = False
        print("Connection Closed")

        # Stop the movement of all actuators & motors on the rover.
        # takes the form of a special flag command to the arduino.

    def send_all_stop(self):
        print("Rover Stopped")
        return True

        # Designate the state of the rover to be sent to the low-level hardware.
        # Float, Float, Bool, Bool

    def send_rover_command(self, in_steer_angle, in_velocity, in_hopper_grasp, in_hopper_up):
        print("Sending Rover Command: ")
        print("============================")
        print("Steering Angle: " + str(in_steer_angle))
        print("In Velocity: " + str(in_velocity))
        print("Hopper Grasp: " + str(in_hopper_grasp))
        print("Hopper Up: " + str(in_hopper_up))
        return True

        # Check measured state of actuators & sensors
        # this must be called repeatedly to get an accurate state of the rover.

    def check_rover_status(self):
        # only check status if the connection is open.
        if self.isOpen:  # read some bytes from the arduino. It's response is 37 bytes in length.
            if 1:  # first number is correct, then parse the message.
                right_velocity = random.randrange(0, 100) / 100
                left_velocity = random.randrange(0, 100) / 100
                # angleVelocity = socket.ntohl(np.float32(msgBuffer[8:13])) #unused
                x_pos = random.randrange(-100, 100)
                y_pos = random.randrange(-100, 100)
                heading = random.randrange(0, 100) / 100 * 360
                battery_volt = random.randrange(0, 100)
                ir_elevation = random.randrange(0, 100)
                ir_heading = random.randrange(0, 100) / 100 * 360
                # status_byte = msgBuffer[37]  #unused.
                is_valid = True

                print("Rover Status: ")
                print("===========================================")
                print("Valid: " + str(is_valid))
                print("Battery Voltage: " + str(battery_volt))
                print("X-Pos: " + str(x_pos))
                print("Y-Pos: " + str(y_pos))
                print("Heading: " + str(heading))
                print("Left Velocity: " + str(left_velocity))
                print("Right Velocity: " + str(right_velocity))
                print("IR Heading: " + str(ir_heading))
                print("IR Elevation: " + str(ir_elevation))
                return is_valid, battery_volt, x_pos, y_pos, heading, left_velocity, right_velocity, ir_heading, ir_elevation
            else:
                print("Status check failed")
                return False
        else:
            print("Status check failed")
            return False
