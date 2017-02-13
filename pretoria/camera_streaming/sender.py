import cv2
import socket
import io
import struct

# The capture from the webcam
capture = cv2.VideoCapture(0)

# Network Info
sock = socket.socket()
host = socket.gethostname()             # This should be the IP or Name of the "Server"
port = 60000                            # The port you want to connect to

sock.connect(('127.0.0.1', port))       # Connects to the "server"
connection = sock.makefile('wb')        # Creates a file like object to which the stream will be written.

stream = io.BytesIO()                   # The byte stream in which the frame will be written.

# Allows the camera to adapt to light exposure.
# The value in the range() indicates how many frames you'd like to "Throw Away"
for _ in range(40):
    frame = capture.read()


while True:
    # Reads a frame from the webcam.
    # The "_" is used to show that it is not going to be used.
    # Will only contain a bool value anyway.
    _, frame = capture.read()
    stream = io.BytesIO(frame)                              # Conversion of the frame to bytes.

    # This is where the stream gets written to the file-like object created earlier.
    # The stream is packed into a struct. Where "<L" means; "How it's packed".
    # And the "stream.seek(0, 2)" determines the size
    connection.write(struct.pack('<L', stream.seek(0, 2)))
    # Flushes the data out of the Internal Buffer to the OS Buffer,
    # allowing the data to be read by other applications etc.
    connection.flush()
    # Moves the pointer to the start of the stream.
    stream.seek(0)
    # I think this is used to specify the End Of File (EOF),
    # or to signify that an entire frame has been send.
    connection.write(stream.read())
    # "Resets" the stream to get it ready to send the next frame.
    stream.truncate()

    # Only shows the frame that was sent.
    # Use "q" to exit the application.
    cv2.imshow('Client', frame)
    k = cv2.waitKey(5)
    if k == ord('q') & 0xFF:
        break

# Closes streams and connections
stream.close()
sock.close()
cv2.destroyAllWindows()             # Really?
capture.release()                   # Releases the webcam to free up resources.