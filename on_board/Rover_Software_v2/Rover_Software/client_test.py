import json
import socket

# used to test the sending and receiving of JSON files

# creates a new socket
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# sets the address and port nr of the server
SERVER = 'localhost'
PORT = 5555


# creates a random command to be sent to the server
def random_command():
    import json
    import random
    return json.loads('{"MovementX": ' + str(random.randrange(0, 100)/100) + ',' +
                      '"MovementY": ' + str(random.randrange(0, 100) / 100) + ',' +
                      '"EStopStatus": ' + str(bool(random.getrandbits(1))) + ',' +
                      '"allStop": ' + str(bool(random.getrandbits(1))) + ',' +
                      '"HopperGrasp": ' + str(bool(random.getrandbits(1))) + ',' +
                      '"HopperDown": ' + str(bool(random.getrandbits(1))) + '')

while 1:
    try:
        # attempts to connect to the given address and port
        socket.connect((SERVER, PORT))
        reply = socket.recv(4096).decode()
        print("Last Rover Status : ")
        print("==================================")
        print(reply)
        print("==================================")
        while 1:
            # sets a predetermined example JSON object
            json_obj = random_command()
            j = input('$- Press enter to send command >> ')
            if j == 'quit':
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
            reply = socket.recv(4096).decode()
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



