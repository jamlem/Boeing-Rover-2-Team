import json
from Handlers import file_handler as log

'''
Used to store the data that will be sent to the rover
Methods for converting to and from JSON files
Example JSON:
{
    "all_stop": false,
    "angle": 100.0,
    "e_stop": false,
    "hopper_down": true,
    "hopper_grasp": true,
    "velocity": 100.0
}
'''


class RoverCommand:
    # initializes a rover command object, with immobility being the default
    def __init__(self, angle=0, velocity=0, e_stop=False, all_stop=False, hopper_grasp=False, hopper_up=False):
        self.angle = angle
        self.velocity = velocity
        self.e_stop = e_stop
        self.all_stop = all_stop
        self.hopper_grasp = hopper_grasp
        self.hopper_up = hopper_up

    # gets command values from JSON object
    def from_json(self, json_obj):
        try:
            self.angle = float(json_obj['MovementX'])
            self.velocity = float(json_obj['MovementY'])
            self.e_stop = bool(json_obj['EStopStatus'])
            self.all_stop = bool(json_obj['allStop'])
            self.hopper_grasp = bool(json_obj['HopperGrasp'])
            self.hopper_up = not bool(json_obj['HopperDown'])
        except Exception as e:
            log.log_error(e)
            self.__init__()

    # sends command values to the interface
    def send(self, conn):
        try:
            if self.e_stop:
                print(">> EMERGENCY - Stopping Rover")
                conn.send_emergency_stop()
            elif self.all_stop:
                print(">> Stopping Rover")
                conn.send_stop()
            else:
                conn.send_rover_command(self.angle, self.velocity, self.hopper_grasp, self.hopper_up)
        except Exception as e:
            self.__init__()
            log.log_error(e)

    # converts the command to a JSON object
    def to_json(self):
        return json.loads(json.JSONEncoder().encode(self.__dict__))
