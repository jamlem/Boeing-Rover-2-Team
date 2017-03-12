import socket
import json_handler
import json

# used to test the sending and receiving of JSON files

# creates a new socket
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# sets the address and port nr of the server
SERVER = 'localhost'
PORT = 5555

while 1:
    try:
        # attempts to connect to the given address and port
        socket.connect((SERVER, PORT))
        # print(socket.recv(4096).decode())
        while 1:
            # sets a predetermined example JSON object
            json_obj = json_handler.json_client_example()
            j = input('$- Press enter to send data >> ')
            # socket.send(j.encode())
            print("Sending : ")
            print("==================================")
            # sends the example JSON object
            socket.send(json.dumps(json_obj).encode())
            # displays the object that was sent
            json_handler.pretty_print(json_obj)
            print("==================================")
            # receive and display the JSON object form the server
            reply = socket.recv(4096).decode()
            json_handler.pretty_print(json.loads(reply))
            if j == 'quit':
                break
        # closes the socket
        socket.close()
    except Exception as e:
        print(str(e))
        break
    finally:
        socket.close()