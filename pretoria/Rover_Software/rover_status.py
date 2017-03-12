import json
'''
Used to store the data that will be sent to the client
Represents the status of the Rover
Methods for converting to and from JSON files
Example JSON:
{
    "battery_volt": 0,
    "heading": 0,
    "ir_elevation": 0,
    "ir_heading": 0,
    "is_valid": false,
    "left_velocity": 0,
    "right_velocity": 0,
    "x_pos": 0,
    "y_pos": 0
}
'''


class RoverStatus:

    def __init__(self, is_valid=False, battery_volt=0, x_pos=0, y_pos=0, heading=0, left_velocity=0, right_velocity=0, ir_heading=0, ir_elevation=0):
        self.is_valid = is_valid
        self.battery_volt = battery_volt
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.heading = heading
        self.left_velocity = left_velocity
        self.right_velocity = right_velocity
        self.ir_heading = ir_heading
        self.ir_elevation = ir_elevation

    def from_json(self, json_obj):
        self.is_valid = json_obj["is_valid"]
        self.battery_volt = json_obj["battery_volts"]
        self.x_pos = json_obj["x_pos"]
        self.y_pos = json_obj["y_pos"]
        self.heading = json_obj["heading"]
        self.left_velocity = json_obj["left_velocity"]
        self.right_velocity = json_obj["right_velocity"]
        self.ir_heading = json_obj["ir_heading"]
        self.ir_elevation = json_obj["ir_elevation"]

    def to_json(self):
        return json.loads(json.JSONEncoder().encode(self.__dict__))


