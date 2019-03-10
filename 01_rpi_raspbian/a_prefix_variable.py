# pixhawk connection                    # parameter to connect raspberry pi with pixhawk
connection = "/dev/ttyS0"               # when connecting to pixhawk via serial connection
timeout = 30                            # how long in second dronekit should keep reconnect
baud = 57600                            # baudrate for communicating with pixhawk

# transmission control protocol         # setting for tcp connection
pc = "192.168.2.105"                    # computer ip address
rpi = "192.168.2.107"                   # raspberry pi ip address
video = 8000                            # video port
rangefinder = 8002                      # rangefinder port
controller = 8004                       # client port

# raspberry pi camera module            # camera module setting
x = 320                                 # camera x-axis size
y = 240                                 # camera y-axis size
fps = 30                                # camera frame per second