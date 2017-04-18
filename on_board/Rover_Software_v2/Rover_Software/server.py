#! /usr/bin/python

import sys

from Handlers import file_handler as log
from Server import server_handler as server

# creates new server object that will interface with the connection object
try:
    server = server.ServerHandler()
except Exception as e:
    log.log_error(e)
    sys.exit()

while 1:
    try:
        server.open_rover_connection()  # opens the connection between the server and the interface
        server.start()  # starts handling client requests
        server.close_rover_connection()  # closes rover connection when the server stops

    except Exception as e:
        log.log_error(e)
        server.restart()
        pass

