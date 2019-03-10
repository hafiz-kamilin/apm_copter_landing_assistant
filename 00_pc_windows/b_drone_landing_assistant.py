#!/usr/bin/env python3
# -*- coding: utf-8 -*-  

# setting up modules used in the program
import a_prefix_variable as apv
from pygame.locals import *
from socket import socket
import pygame.display
import numpy as np
import threading
import pygame
import socket
import time
import cv2
import sys
import os

# threading 1; create a class for raspberry pi camera module server
class VideoStreamServer(threading.Thread):

    # initialize threading 1, server socket address and port
    def __init__(self, host1, port1):

        # server socket and port
        self.server_socket = socket.socket()
        self.server_socket.bind((host1, port1))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.connection = self.connection.makefile('rb')
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        # maximum red color range in ycrcb colouring
        self.upper_red = np.array(apv.upred)
        # minimum red color range in ycrcb colouring
        self.lower_red = np.array(apv.lowred)
        # execute server receiving
        self.receiving()

    # when connection with client is established
    def receiving(self):

        try:

            # need bytes here
            stream_bytes = b' '
            # LatchingSwitch class is now switch
            switch = LatchingSwitch()
            
            # while loop
            while True:

                # if kill switch for threading 1 is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # get start time
                start = time.time()
                # find first and last byte of jpg stream
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                # if first and last byte is not -1
                if ((first != -1) and (last != -1)):

                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    # turn jpg data into something understandable to opencv
                    rgb = cv2.imdecode(np.frombuffer(jpg, dtype = np.uint8), cv2.IMREAD_COLOR)
                    # convert frame coloring to ycrcb
                    ycrcb = cv2.cvtColor(rgb, cv2.COLOR_BGR2YCrCb)
                    # mask all colour except red
                    mask = cv2.inRange(ycrcb, self.lower_red, self.upper_red)
                    # dilate outer pixels of an object in mask
                    mask = cv2.dilate(mask, None, iterations = 2)
                    # find contours in the mask
                    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cnts = imutils.grab_contours(cnts)
                    # initialize (x, y) center of the ball
                    center = None

                    # if countour was found and the distance from the ground is more than 100 cm
                    if ((len(cnts) > 0) and (RangeFinderServer.distance > 100)):

                        # find the largest contour in the mask
                        c = max(cnts, key = cv2.contourArea)
                        # calculate the minimum enclosing circle
                        ((x, y), radius) = cv2.minEnclosingCircle(c)
                        # calculate the centroid
                        M = cv2.moments(c)
                        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                        # if the radius meets a minimum size
                        if (radius > 15):

                            # draw the circle overlay
                            cv2.circle(rgb, (int(x), int(y)), int(radius), (0, 0, 255), 2)
                            # draw the centroid overlay
                            cv2.circle(rgb, center, 5, (0, 0, 255), -1)
                            # center pinpoint result
                            print ("The circle's center is located at point x-axis: %s, y-axis: %s." % (center[0], center[1]))

                    # distance from the ground overlay
                    cv2.putText(rgb, "Ground distance: {} [cm]".format(RangeFinderServer.distance), (10, 30), cv2.FONT_HERSHEY_DUPLEX, .45, (0, 0, 255), 1)
                    # print time taken to prepare 1 image
                    print ("Frame take %.3f [s] to complete" % (time.time() - start))
                    # display the data stream as video
                    cv2.imshow("To quit press [q].", rgb)

                    # to close opencv windows press [q]
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        
                        # turn on the kill switch 2
                        switch.killswitch2()
                        # break from while loop
                        break

        except:

            # do nothing
            pass

        else:

            # quit video server nicely
            self.connection.close()
            self.server_socket.close()

# threading 2; create a class for lidar rangefinder server
class RangeFinderServer(threading.Thread):
    
    # initialize shared data variable
    distance = None

    # initialize threading 2, server socket address and port
    def __init__(self, host2, port2):

        # assign value to shared data variable
        RangeFinderServer.distance = 0
        # server socket and port
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host2, port2))
        self.server_socket.listen(0)
        self.connection, self.client_address = self.server_socket.accept()
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        # execute server receiving
        self.receiving()

    # when connection with client is established
    def receiving(self):

        try:

            # while loop
            while True:

                # if kill switch for threading 2 is activated
                if (LatchingSwitch.tr_alive != True):

                    # break from while loop
                    break

                # receive the distance reading from the client
                RangeFinderServer.distance = int(self.connection.recv(1024).decode())
                # print out the distance
                print ("Distance from the ground is %d [cm]" % RangeFinderServer.distance)

        except:

            # do nothing
            pass

        else:

            # quit rangefinder server nicely
            self.connection.close()
            self.server_socket.close()

# step 1; system compatibility check
class CompatibilityCheck(object):

    # check os compatibility
    if (os.name != 'nt'):

        print ("\nThis codes only compatible with Windows OS!\n")
        exit()

    # check python environment compatibility
    if (sys.version_info[0] < 3):

        print ("\nThis codes only compatible with Python 3 environment!\n")
        exit()

# step 2; initialize latching switch to communicate with threading 1, 2, 3
class LatchingSwitch(object):

    # initialize switches variables
    tr_alive = None

    # initialize switches value
    def __init__(self):

        # assign switches value to true
        LatchingSwitch.tr_alive = True

    # change switches value
    def killswitch1(self):

        # assign switches value to false
        LatchingSwitch.tr_alive = False

    # change switches value
    def killswitch2(self):

        # assign switches value to None
        LatchingSwitch.tr_alive = None

# step 3; control latching switch condition and manage individual threading 1, 2, 3
class ThreadingManager(object):

    # LatchingSwitch class is now switch
    switch = LatchingSwitch()

    try:

        # clear the screen
        os.system("cls")
        # print out info for user
        print ("This Python program will act as an interface for APM: Copter to assist the user to find")
        print ("the landing mark by creating an overlay on top of the video stream.")
        print ("\nTo stop before TCP connection is established press [CTRL] + [c] on console, to stop")
        print ("after TCP connection is established press [q] on Pygame or OpenCV windows.")
        # get user input
        input ("\nTo start press [Enter].")
        # set classes as threadings
        tr1 = threading.Thread(target = VideoStreamServer, args = (apv.pc, apv.video))
        tr2 = threading.Thread(target = RangeFinderServer, args = (apv.pc, apv.rangefinder))
        # set threadings as daemon
        tr1.daemon = True
        tr2.daemon = True
        # set classes as threadings
        tr1.start()
        tr2.start()
        # print out info for user
        print ("\nThreading start, waiting connection from RPi side.\n")

        # check threading 1, 2 to see if it is alive or not
        while True:

            # if program ended nicely
            if (LatchingSwitch.tr_alive == None):

                # break from while loop
                break

            # if threading1 is dead
            if ((tr1.is_alive() != True) and (tr2.is_alive() == True)):

                # print the message
                print ("\nVideoStreamServer threading ended prematurely.\n")
                # raise exception
                raise Exception

            # else if threading2 is dead
            elif ((tr1.is_alive() == True) and (tr2.is_alive() != True)):

                # print the message
                print ("\nRangeFinderServer threading ended prematurely.\n")
                # raise exception
                raise Exception

            # else if threading1 and threading2 are dead
            elif ((tr1.is_alive() != True) and (tr2.is_alive() != True)):

                # print the message
                print ("\nTCP connection was terminated on Raspberry Pi side.\n")
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

        # turn on the kill switch 1
        switch.killswitch1()
        # give time for threading to close
        time.sleep(3)
        # print out message
        print ("\nProgram ended.\n")

# initiator
if __name__ == '__main__':

    # step 1; run compatibility check sequence
    CompatibilityCheck()
    # step 2; initialize latching switch
    LatchingSwitch()
    # step 3; initialize threading
    ThreadingManager()