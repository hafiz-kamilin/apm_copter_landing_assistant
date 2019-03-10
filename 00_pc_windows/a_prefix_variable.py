# transmission control protocol         # setting for tcp connection
pc = "192.168.2.105"                    # computer ip address
rpi = "192.168.2.107"                   # raspberry pi ip address
video = 8000                            # video port
rangefinder = 8002                      # rangefinder port
controller = 8004                       # client port

# image processing                      # masking parameter
upred = [145, 200, 120]                 # maximum red color range in ycrcb colouring
lowred = [ 10, 170,  90]                # minimum red color range in ycrcb colouring