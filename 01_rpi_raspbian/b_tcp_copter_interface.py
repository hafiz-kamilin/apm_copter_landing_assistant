#!/usr/bin/env python2
# -*- coding: utf-8 -*-  

# setting up modules used in the program
from __future__ import print_function
import a_prefix_variable as apv
from dronekit import connect
from socket import socket
import threading
import picamera
import socket
import struct
import time
import sys
import os
import io

# threading 1; create a class for camera (video) client
class VideoStreamClient(threading.Thread):

    # initialize threading 1, client socket address and port
    def __init__(self, host1, port1):

        # client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        # client condition
        self.connected = False 

        # while client haven't connected to server
        while not (self.connected):

            try:

                # reconnecting to server
                self.client_socket.connect((host1, port1))
                self.connection = self.client_socket.makefile('wb')
                self.connected = True

            except Exception as e:

                # if failed try again
                pass
        
        # execute client sending
        self.sending()

    # when connection with server is established
    def sending(self):

        try:
                    
            # initialize raspberry pi camera module parameter
            with picamera.PiCamera() as camera:

                # video resolution
                camera.resolution = (apv.x, apv.y)
                # frames/second     
                camera.framerate = apv.fps
                # give 2 [s] for camera module to initilize
                time.sleep(2)                       
                start = time.time()
                stream = io.BytesIO()

                # send jpeg format video stream
                for foo in camera.capture_continuous(stream, 'jpeg', use_video_port = True):

                    # get start time
                    start = time.time()

                    # if kill switch for threading 1 is activated
                    if (LatchingSwitch.tr_alive != True):

                        # break from for loop
                        break

                    # pack the jpeg data into struct
                    self.connection.write(struct.pack('<L', stream.tell()))
                    self.connection.flush()
                    stream.seek(0)
                    self.connection.write(stream.read())

                    # after 10 minutes
                    if (time.time() - start > 600):
                        
                        # break from for loop
                        break

                    # seek and truncate stream
                    stream.seek(0)
                    stream.truncate()

                    # print time taken to prepare 1 image
                    print ("Frame take %.3f [s] to complete" % (time.time() - start))

            # write the terminating 0-length to the connection to let the video server know we're done
            self.connection.write(struct.pack('<L', 0))

        except:

            # do nothing
            pass

        else:
            
            # quit the raspberry pi camera module client threading nicely
            self.connection.close()
            self.client_socket.close()

# threading 2; create a class for rangefinder client
class RangeFinderClient(threading.Thread):

    # initialize threading 2, client socket address and port
    def __init__(self, host2, port2):

        # client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection = None
        # client condition
        self.connected = False 

        # while client haven't connected to server
        while not (self.connected):

            try:

                # reconnecting to server
                self.client_socket.connect((host2, port2))
                self.connection = self.client_socket.makefile('wb')
                self.connected = True

            # if failed
            except Exception as e:

                # if kill switch is activated
                if (LatchingSwitch.tr_alive != True):

                    # stop trying
                    self.connected = True

                # if kill switch is not activated
                else:

                    # try again
                    pass
        
        # execute client sending
        self.sending()

    # when connection with server is established
    def sending(self):

        try:
            
            # while loop
            while True:

                # if kill switch for threading 2 is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # get distance reading from rangefinder
                measured_distance = int(ConnectPixhawk.serial.rangefinder.distance * 100)
                # print distance reading
                print ("Distance in front is %d [cm]" % measured_distance)
                # send distance reading to lidar rangefinder server
                self.client_socket.send(str(measured_distance).encode())
                # sleep for 0.1 [s]
                time.sleep(0.1)

        except:

            # do nothing
            pass

        else:
            
            # quit lidar rangefinder client nicely
            self.client_socket.close()

# step 1; system compatibility check
class CompatibilityCheck(object):

    # check os compatibility
    if (os.name == 'nt'):

        print ("\nThis codes only compatible with Linux OS!\n")
        exit()

    # check python environment compatibility
    if (sys.version_info[0] > 2):

        print ("\nThis codes only compatible with Python 2 environment!\n")
        exit()

# step 2; connect raspberry pi with pixhawk
class ConnectPixhawk(object):

    # suppressing messages or errors from dronekit
    def suppress_print(x):

        # do nothing
        pass

    # establishing connection between raspberry pi and pixhawk
    serial = connect(apv.connection, heartbeat_timeout = apv.timeout, baud = apv.baud, status_printer = suppress_print)

# step 3; initialize latching switch to communicate with threading 1, 2, 3, 4
class LatchingSwitch(object):

    # initialize switches variables
    tr_alive = None

    # initialize switches value
    def __init__(self):

        # assign switches value to true
        LatchingSwitch.tr_alive = True

    # change switches value
    def killswitch(self):

        # assign switches value to false
        LatchingSwitch.tr_alive = False

# step 4; control latching switch condition and manage individual threading 1, 2, 3, 4
class ThreadingManager(object):

    try:

        # LatchingSwitch class is now switch
        switch = LatchingSwitch()
        # clear the screen
        os.system("clear")
        # print out info for user
        print ("This Python program will act as an interface for APM: Copter to assist the user to find")
        print ("the landing mark by creating an overlay on top of the video stream.")
        print ("To stop at any time given press [CTRL] + [c].")
        # get user input
        raw_input ("\nTo start press [Enter].")
        # set classes as threadings
        tr1 = threading.Thread(target = VideoStreamClient, args = (apv.pc, apv.video))
        tr2 = threading.Thread(target = RangeFinderClient, args = (apv.pc, apv.rangefinder))
        # set threadings as daemons
        tr1.daemon = True
        tr2.daemon = True
        # start the threading
        tr1.start()
        tr2.start()
        # print out info for user
        print ("\nThreading start, waiting connection from PC side.\n")
        # take 5 seconds break
        time.sleep(5)

        # check threading 1, 2 to see if it is alive or not
        while True:

            # if threading1 is dead
            if ((tr1.is_alive() != True) and (tr2.is_alive() == True)):

                # print the message
                print ("\nVideo client threading ended prematurely.\n")
                # raise exception
                raise Exception

            # else if threading2 is dead
            elif ((tr1.is_alive() == True) and (tr2.is_alive() != True)):

                # print the message
                print ("\nRangefinder client threading ended prematurely.\n")
                # raise exception
                raise Exception


            # else if threading1 and threading2 are dead
            elif ((tr1.is_alive() != True) and (tr2.is_alive() != True)):

                # print the message
                print ("\nTCP connection was terminated on PC side.\n")
                # raise exception
                raise Exception

            # stop before looping again in 3 [s]
            time.sleep(3)

    except KeyboardInterrupt:

        # when [CTRL] + [c] is pressed print the message
        print ("\n[CTRL] + [c] is pressed.\n")

    except:

        # when exception is raised print the message
        print ("\nException raised.\n")

    finally:

        # turn on the kill switch
        switch.killswitch()
        # give time for threading to close
        time.sleep(3)
        # close connection between raspberry pi and pixhawk
        ConnectPixhawk.serial.close()
        # print out message
        print ("\nProgram ended.\n")

# initiator
if __name__ == '__main__':

    # step 1; run compatibility check sequence
    CompatibilityCheck()
    # step 2; connecting raspberry pi with pixhawk
    ConnectPixhawk()
    # step 3; initialize latching switch
    LatchingSwitch()
    # step 4; initialize threading
    ThreadingManager()