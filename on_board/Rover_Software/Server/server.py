import _thread
import json
import socket
import sys

from Handlers import json_handler
from Handlers import HW_Interface_Test
from Rover_Classes import rover_command
from Rover_Classes import rover_status

HOST = ''  # shorthand for listen to all
PORT = 5555

try:
    rover_connection = HW_Interface_Test.HWInterfaceTest()
    print("Rover Connection Established")
except Exception as e:
    print(str(e))

# creates streaming socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('>> Socket created')
try:
    s.bind((HOST, PORT))  # initializes the socket with the given port and address
except socket.error as e:
    print('>> Bind failed. Error Code : ' + str(e))
    sys.exit()

print('>> Socket bind complete')
s.listen(10)  # listens for a connection
print('>> Socket now listening')

# handles a received request as a JSON string


def handle_request(conn, data, rover_connection):

    # create a new RoverCommand object from the incoming JSON file
    command = rover_command.RoverCommand()
    command.from_json(json.loads(data.decode()))

    # displays received JSON object
    print("Data Received: ")
    print("==================================")
    json_handler.pretty_print(command.to_json())
    print("==================================")

    command.send(rover_connection)

    status = rover_status.RoverStatus()
    status.get_status(rover_connection)

    # sends and displays rover status
    print("Sending: ")
    print("==================================")
    conn.sendall(json.dumps(status.to_json()).encode())
    json_handler.pretty_print(status.to_json())
    print("==================================")

# listens and handles incoming data from the client


def client_thread(conn, rover_connection):
    # conn.sendall(str.encode('>> Connection to server established\n'))
    while True:
        try:
            # receives data from the client
            data = conn.recv(4096)
            if not data:
                break
            # sends data to the handler
            _thread.start_new_thread(handle_request, (conn, data, rover_connection))
            # breaks if data fails

        except Exception as e:
            # catches any possible exception and stops the rover
            print(str(e))
            break

    rover_connection.send_all_stop()
    rover_connection.close_connections()
    conn.close()

while 1:
    # accepts incoming connection
    conn, address = s.accept()
    # displays client's IP and port connected to
    print('>> Connected with ' + address[0] + ':' + str(address[1]))
    rover_connection.open_connections()
    # starts accepting requests from the connected client
    client_thread(conn, rover_connection)

# closes the socket
s.close()

