import socket
import struct
import io
import picamera
import time

capture = picamera.PiCamera()           # The variable to which the Pi Cam is assigned.

# Network Info
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#host = socket.gethostname()  # This should be the IP or Name of the "Server"
host = '10.0.0.6'
port = 60000                            # The port you want to connect to

sock.connect((host, port))       # Connects to the "server"
connection = sock.makefile('wb')        # Creates a file like object to which the stream will be written.
           # The byte stream in which the frame will be written.

with capture as camera:
    camera.vflip = True                 # This can be false or true, depending on the orientation of the Pi Cam
    camera.resolution = (384, 384)      # Resolution in which the images should be captured.
    cameraframerate = 32                # Framerate of the camera
    time.sleep(2)
    stream = io.BytesIO()        
    try:
        while True:
            # The following will be done for every frame captured by the Pi Cam
            # Writes every frame to a stream. Converts it to bytes automatically.
            # 'bgr' is the format in which the image is captured
            # The last parameter states whether the dedicated video port should be used.
            for frame in camera.capture_continuous(stream, 'bgr', use_video_port = True):
                # This is where the stream gets written to the file-like object created earlier.
                # The stream is packed into a struct. Where "<L" means; "How it's packed".
                # And the "stream.seek(0, 2)" determines the size
                connection.write(struct.pack('<L', stream.tell()))
                # Flushes the data out of the Internal Buffer to the OS Buffer,
                # allowing the data to be read by other applications etc.
                connection.flush()
                # Moves the pointer to the start of the stream.
                stream.seek(0)
                # I think this is used to specify the End Of File (EOF),
                # or to signify that an entire frame has been send.
                connection.write(stream.read())
                # "Resets" the stream to get it ready to send the next frame.
                stream.seek(0)
                stream.truncate()
        connection.write(struct.pack('<L', 0))
    finally:
        # Clothes everything and frees up the Pi Cam
        connection.close()
        sock.close()
        capture.close()
