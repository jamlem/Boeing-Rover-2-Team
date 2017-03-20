import _thread
import json
import socket
import sys

from Handlers import json_handler
from Rover_Classes import rover_command
from Rover_Classes import rover_status

HOST = ''  # shorthand for listen to all
PORT = 5555

# creates streaming socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('>> Socket created')
try:
    s.bind((HOST, PORT)) # initializes the socket with the given port and address
except socket.error as e:
    print('>> Bind failed. Error Code : ' + str(e))
    sys.exit()
     
print('>> Socket bind complete')
s.listen(10) # listens for a connection
print('>> Socket now listening')

# handles a received request as a JSON string


def handle_request(conn, data):

    # create a new RoverCommand object
    command = rover_command.RoverCommand()
    # converts the incoming JSON file to a RoverCommand object
    command.from_json(json.loads(data.decode()))
    print("Data Received: ")
    print("==================================")
    # displays the RoverCommand object as a JSON file
    json_handler.pretty_print(command.to_json())
    print("==================================")
    # creates a RoverStatus object
    status = rover_status.RoverStatus()
    print("Sending: ")
    print("==================================")
    # returns the RoverStatus object as a JSON to the client
    conn.sendall(json.dumps(status.to_json()).encode())
    # displays the RoverStatus object as a JSON file
    json_handler.pretty_print(status.to_json())
    print("==================================")

# listens and handles incoming data from the client


def client_thread(conn):
    # conn.sendall(str.encode('>> Connection to server established\n'))
    while True:
        try:
            # receives data from the client
            data = conn.recv(4096)
            # sends data to the handler
            _thread.start_new_thread(handle_request, (conn, data))
            # breaks if data fails
            if not data:
                break
        except Exception as e:
            print(str(e))
            break
            # closes connection
    conn.close()

while 1:
    # accepts incoming connection
    conn, address = s.accept()
    # displays client's IP and port connected to
    print('>> Connected with ' + address[0] + ':' + str(address[1]))
    # starts accepting requests from the connected client
    client_thread(conn)

# closes the socket
s.close()

