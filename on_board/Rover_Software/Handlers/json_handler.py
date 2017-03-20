# a few basic JSON operations
# gives an example of the expected JSON object


def json_client_example():
    import json
    return json.loads('{'
                      '"MovementX": 100.0,'
                      ' "MovementY": 100.0,'
                      ' "EStopStatus": false,'
                      ' "HopperGrasp": true,'
                      ' "HopperDown": true'
                      '}')


def json_client_example2():
    import random
    from Rover_Classes import rover_command
    command = rover_command.RoverCommand(random.randrange(0, 100),
                                         random.randrange(0, 100),
                                         bool(random.getrandbits(1)),
                                         bool(random.getrandbits(1)),
                                         bool(random.getrandbits(1)))
    return command.to_json()


# displays a JSON object
def pretty_print(json_obj):
    import json

    print(json.dumps(json_obj, sort_keys=True, indent=4))

