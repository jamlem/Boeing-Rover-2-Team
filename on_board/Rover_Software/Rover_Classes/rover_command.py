import json
'''
Used to store the data that will be sent to the rover
Methods for converting to and from JSON files
Example JSON:
{
    "angle": 100.0,
    "e_stop": false,
    "hopper_down": true,
    "hopper_grasp": true,
    "velocity": 100.0
}
'''


class RoverCommand:

    def __init__(self, angle=0, velocity=0, e_stop=False, hopper_grasp=False, hopper_down=False):
        self.angle = angle
        self.velocity = velocity
        self.e_stop = e_stop
        self.hopper_grasp = hopper_grasp
        self.hopper_down = hopper_down

    def from_json(self, json_obj):
        self.angle = json_obj['MovementX']
        self.velocity = json_obj['MovementY']
        self.e_stop = json_obj['EStopStatus']
        self.hopper_grasp = json_obj['HopperGrasp']
        self.hopper_down = json_obj['HopperDown']

    def send(self, conn):
        if (type(self.e_stop) == 'bool') and self.e_stop:
            print("Stopping Rover")
            conn.send_all_stop()
        else:
            if (not type(self.angle) == 'float') or (not type(self.velocity) == 'float') or (not type(self.hopper_grasp) == 'bool') or (not type(self.hopper_down) == 'bool'):
                self.__init__()

            if not conn.send_rover_command(self.angle,
                                           self.velocity,
                                           self.hopper_grasp,
                                           not self.hopper_down):
                print("Execution Failed")

    def to_json(self):
        return json.loads(json.JSONEncoder().encode(self.__dict__))
