import cv2
import socket
import struct
import io
from PIL import Image
import numpy

# Network Info
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()                         # Gets the host name on which the server is located.
port = 60000

# Binds to a Host And Port.
# Might be wise to bind to the Host: "0.0.0.0" so that the server listens on all interfaces.
# Not sure if that would be best practice though.
sock.bind(('0.0.0.0', port))
sock.listen(0)                                      # Listens for a connection
connection = sock.accept()[0].makefile('rb')        # Creates a file like object from which the stream will be read.
stream = io.BytesIO()                               # Stream in which the data of the frame sent will be.

while True:
    image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]          # Length (in bytes) of the frame

    # This writes the data found in the file-like object to the stream.
    # Image length is used to read the exact amount of bytes from the file
    stream.write(connection.read(image_len))
    # Moves pointer to the start of the stream
    stream.seek(0)

    image_data = stream.getvalue()                                          # Really?
    # Converts the data in "image_data" to an image, using the PIL module.
    # Hint:
    # 1) Make sure the format ("RGB" in this case) is the same format of the image that was sent.
    # Might not be true for the Pi Camera though
    # 2) Make sure that the resolution of the image is the same.
    image_recv = Image.frombytes('RGB', (384, 384), image_data)
    # Converts the PIL image ("image_recv") to a numpy array, so it can be interpreted by the Open CV module.
    img_cv = numpy.array(image_recv)

    # Displays the image that was received.
    # Use the "q" key to quit the application
    cv2.imshow('Server', img_cv)
    k = cv2.waitKey(5)
    if k == ord('q') & 0xFF:
        break

# Closes stuff and things.
cv2.destroyAllWindows()
connection.close()
sock.close()
