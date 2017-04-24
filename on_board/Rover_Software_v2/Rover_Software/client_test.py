#! /usr/bin/python

import json
import socket
import random

# used to test the sending and receiving of JSON files

# creates a new socket
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# sets the address and port nr of the server
# 'localhost'
SERVER = '127.0.0.1'
PORT = 5558


# creates a random command to be sent to the server
def random_command():
    coolStr = '{"MovementX": ' + str(random.randrange(0, 100)/100) + ',' + '"MovementY": ' + str(random.randrange(0, 100) / 100) + ',' + '"EStopStatus": ' + str(bool(random.getrandbits(1))).lower() + ',' + '"allStop": ' + str(bool(random.getrandbits(1))).lower() + ',' + '"HopperGrasp": ' + str(bool(random.getrandbits(1))).lower() + ',' + '"HopperDown": ' + str(bool(random.getrandbits(1))).lower() + '}'
    print(str(coolStr))
    data = json.loads(coolStr)
    return data


def fixed_command():
    coolStr = '{"MovementX": ' + str(-25.0) + ',' + '"MovementY": ' + str(-20.0) + ',' + '"EStopStatus": false, ' + '"allStop": false, ' + '"HopperGrasp": false,' + '"HopperDown": false }'
    print(str(coolStr))
    data =  json.loads(coolStr)
    return data

while 1:
    try:
        # attempts to connect to the given address and port
        # test_obj = random_command()
        socket.connect((SERVER, PORT))
        reply = socket.recv(4096).decode()
        print("Last Rover Status : ")
        print("==================================")
        print(reply)
        print("==================================")
        while 1:
            # sets a predetermined example JSON object
            json_obj = fixed_command()
            j = input('$- Press enter to send command >> ')
            if str(j) == 'quit':
                break
            # socket.send(j.encode())
            print("Sending : ")
            print("==================================")
            # sends the example JSON object
            socket.send(json.dumps(json_obj).encode())
            # displays the object that was sent
            print(json.dumps(json_obj))
            print("==================================")
            # receive and display the JSON object form the server
            repdata = socket.recv(4096)
            print(str(len(repdata)))
            reply = repdata.decode()
            print("Rover Status : ")
            print("==================================")
            print(reply)
            print("==================================")

        # closes the socket
        socket.close()
    except Exception as e:
        print(str(e))
        break
    finally:
        socket.close()



