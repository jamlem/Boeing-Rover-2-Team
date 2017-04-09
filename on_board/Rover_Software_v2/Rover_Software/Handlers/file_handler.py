import os
#
# Used to read and write text to and from text and JSON files
# Used for logging of errors, and history of commands and status


# appends text to given file
def log_text(filename, string):
    try:
        import datetime
        # file_path = os.path.join(os.path.dirname(__file__), filename)
        file = open(filename, "a+")
        file.write(str(datetime.datetime.now()) + "\n")
        file.write(string + "\n")
        file.write(">\n")
        file.close()
    except Exception as e:
        print(str(e))


# writes the last position of the rover as a JSON file
def update_last_status(status):
    import json
    try:
        # file_path = os.path.join(os.path.dirname(__file__), '/Logs/last_status.json')
        with open('./Logs/last_status.json', "w+") as file:
            json.dump(status.to_json(), file)
            file.close()
    except Exception as e:
        log_error(e)


# returns the last status of the rover in the JSON file
# returns NULL if no last status is saved
def get_last_status():
    import json
    try:
        # file_path = os.path.join(os.path.dirname(__file__), '/Logs/last_status.json')
        with open('./Logs/last_status.json', "r+") as file:
            json_obj = json.load(file)
            file.close()
            return json_obj
    except Exception:
        return None


# logs an error object
def log_error(e):
    print(str(e))
    log_text('./Logs/errors.txt', str(e))


# logs list of commands sent to the rover
def log_command(command):
    import json
    log_text('./Logs/command_list.txt', json.dumps(command.to_json()))


# logs list of statuses returned from the rover
def log_status(status):
    import json
    log_text('./Logs/status_list.txt', json.dumps(status.to_json()))

