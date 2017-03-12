# a few basic JSON operations
# gives an example of the expected JSON object


def json_client_example():
    import json
    return json.loads('{"MovementX": 100.0, "MovementY": 100.0, "EStopStatus": false, "HopperGrasp": true, "HopperDown": true}')


# displays a JSON object
def pretty_print(json_obj):
    import json

    print(json.dumps(json_obj, sort_keys=True, indent=4))

