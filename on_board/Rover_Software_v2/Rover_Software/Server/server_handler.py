import json
import socket
from Rover_Classes import rover_command
from Rover_Classes import rover_status
from Rover_Classes import rover_exceptions as error
from Handlers import file_handler as log
from Handlers import hardware_interface


class ServerHandler:
    def __init__(self):
        # sets the server address and listening port
        self.host = ''
        self.port = 5558
        # creates a socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # binds the socket to specified host and port
        self.__bind_socket()
        # listens only for a single connection
        self.socket.listen(1)
        # declared for later use
        self.conn = None
        self.address = None
        # hardware interface to be used
        self.rover_connection = hardware_interface.HardwareInterface()
        print(">> Socket Created")

    # opens server connection to rover
    def open_rover_connection(self):
        try:
            self.rover_connection.open_connections()
            print(">> Opening Rover Connection")
        except Exception as e:
            raise e

    # closes server connection to rover
    def close_rover_connection(self):
        try:
            self.rover_connection.close_connections()
            print(">> Closing Rover Connection")
        except Exception as e:
            raise e

    # binds the socket to the specified host and port
    def __bind_socket(self):
        try:
            self.socket.bind((self.host, self.port))
            print(">> Bind Successful")
        except Exception as e:
            raise e

    # waits for a connection and handles requests when a client connects
    def start(self):
        try:
            print(">> Waiting for connection")
            self.conn, self.address = self.socket.accept()  # accepts the incoming client request
            print('>> Connected with ' + self.address[0] + ':' + str(self.address[1]))
            self.conn.sendall(json.dumps(log.get_last_status()).encode())  # returns the last saved status to the client
            while 1:
                # receive data from the client whilst they are still connected
                try:
                    self.__receive_data()
                except Exception as e:
                    # stops the rover when an unexpected error occurs
                    raise e
        except OSError:#Unsure what type of error; raspi is not windows!
            # displays client disconnection and passes through to attempts a reconnect
            print(">> Disconnected from " + self.address[0] + ':' + str(self.address[1]))
            self.rover_connection.send_stop()
            pass
        except error.DataReceiveError:
            print(">> Disconnected from " + self.address[0] + ':' + str(self.address[1]))
            self.rover_connection.send_stop()
            pass
        except Exception as e:
            self.rover_connection.send_emergency_stop()
            raise e

    def __handle_request(self, data):
        # creates a rover command object from incoming byte stream
        command = rover_command.RoverCommand()
        command.from_json(json.loads(data.decode()))

        # displays received JSON object
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(">> Data Received: ")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(json.dumps(command.to_json()))
        print(">> Velocity: " + str(command.velocity))
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        # sends the command to the interface
        try:
            command.send(self.rover_connection)
        except Exception as e:
            log.log_error(e)

        # creates a rover status object from data from the hardware interface
        status = rover_status.RoverStatus()
        status.get_status(self.rover_connection)

        # sends and displays rover status
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(">> Sending: ")
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        self.conn.sendall(json.dumps(status.to_json()).encode())
        print(json.dumps(status.to_json()))
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    # listens and handles incoming data from the client
    def __receive_data(self):
            try:
                # receives data from the client
                print(">> Waiting for request")
                data = self.conn.recv(4096)
                if not data:
                    # raises an error should receiving of data fail
                    raise error.DataReceiveError("Receive data - Input data not valid")
                # sends data to the handler
                self.__handle_request(data)
            except error.DataReceiveError as e:
                raise e
            except Exception as e:
                log.log_error(e)

    # closes the socket and recreates the server object
    def restart(self):
        self.socket.close()
        self.close_rover_connection()
        self.__init__()
