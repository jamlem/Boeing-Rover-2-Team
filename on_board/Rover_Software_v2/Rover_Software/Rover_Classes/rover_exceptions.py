#! /usr/bin/python

#  Jeremy Lim
#  3/25/17
#  Python classes of exceptions, for use in HW_interface.py
#  Edited to be used on server side application


class MessageError(Exception):

    # A string describing the error
    def __init__(self, message):
        self.message = message


class HardwareConnectError(Exception):

    # A string describing the error
    def __init__(self, message):
        self.message = message


class DataReceiveError(Exception):

    def __init__(self, message):
        self.message = message
