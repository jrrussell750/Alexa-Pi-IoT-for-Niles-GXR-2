import time
import datetime
import json
import socket
import logging
import os
import re
from array import *
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

myMQTTClient = AWSIoTMQTTClient("01174A032072300004") #random key, if another connection using the same key is opened the previous one is auto closed by AWS IOT
myMQTTClient.configureEndpoint("a3ci7g5ta9i6w4-ats.iot.us-west-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/pi/AWSIoT/AmazonRootCA1.pem", "/home/pi/AWSIoT/private.pem.key", "/home/pi/AWSIoT/certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2) # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10) # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5) # 5 sec

input_string = ""
zonenum = b"\x00"
inputnum = b"\x00"
navnum = b"\x2C"
count = 0

def customCallback(self, params, packet):
    global input_string
    input_string = packet.payload
    print(input_string)

print ('Initiating IoT Core Topic ...')
Date_Time = datetime.datetime.now()
print(Date_Time)
while (1):
    myMQTTClient.connect()
    myMQTTClient.subscribe("niles/gxr2", 0, customCallback)
    count = 0  # Initialize count to zero

    while (count < 100):  # This loop restarts the connection if no message is received within 1 hour
    
        string_length = len(input_string)
        if (string_length > 0):
            count = 0
            intent = ""
            zone = ""
            device = ""
            index = 1
            time.sleep(1)

            # get current GXR-2 status information
            # status information is collected by a separate C program that runs in the background
            # on the raspberry pi.  The program can be downloaded from github as part of this project
            # see Read_this_file.txt at https://github.com/jrrussell750/Alexa-Pi-IoT-for-Niles-GXR-2

            statusfile = open("GXR2status.txt", "r")
            statusarray = ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]  
            for i in range (0,12):
                statusarray[i] = statusfile.readline()
                print(statusarray[i])
            statusfile.close() 
  
            # parse input https://github.com/jrrussell750/Alexa-Pi-IoT-for-Niles-GXR-2string

            while (chr(input_string[index]) != ':'):
                intent = intent + chr(input_string[index])
                index = index + 1
            index = index + 1
            while (chr(input_string[index]) != ':'):
                zone = zone + chr(input_string[index])
                index = index + 1
            index = index + 1 
            while (chr(input_string[index]) != "\""):
                device = device + chr(input_string[index])
                index = index + 1
        
            # select zone code - used for zone-level commands (setintent or levelintent)
            # you can modify the zone names to match your GXR-2 configuration
 
 
            if((intent=="set") or (intent=="adjust")):
                zonenum = b"\x21"
                if(zone=="1" or zone=="living room"):
                    zonenum = b"\x21"
                    i=6
                elif(zone=="2" or zone=="kitchen"):
                    zonenum = b"\x22"
                    i=7
                elif(zone=="3" or zone=="master bedroom"):
                    zonenum = b"\x23"
                    i=8
                elif(zone=="4" or zone=="patio"):
                    zonenum = b"\x24"
                    i=9
                elif(zone=="5" or zone=="master bath"):
                    zonenum = b"\x25"
                    i=10
                elif(zone=="6" or zone=="basement"):
                    zonenum = b"\x26"
                    i=11
                else:
                    print("No zone found")
                    i=0
                currentlevel = statusarray[i]
            
            #  Open socket to Niles GXR-2

            UDP_IP = "10.100.0.1"
            UDP_PORT = 6001
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
        

            # select device code - used for the set intent
            # You can modify the device names to match your GXR-2 configuration
  
            if((intent=="set")): 
                inputnum = b"\x04"    
                if(device=="1" or device=="a.m. FM"):
                    inputnum = b"\x01"
                elif(device=="2" or device=="1 pens music" or device=="music" ):
                    inputnum = b"\x02"
                elif(device=="3" or device=="TV"):
                    inputnum = b"\x03"
                elif(device=="4" or device=="echo"):
                    inputnum = b"\x04"
                elif(device=="5" or device=="glen"):
                    inputnum = b"\x05"
                elif(device=="6" or device=="John"):
                    inputnum = b"\x06"
                elif(device=="off"):
                    inputnum = b"\x0a"
                else:
                    print("No device found for set intent")
                    
            #  Compose and send message to set the input for a zone in the GXR-2


                MESSAGE = b"\x00\x0e\x00" + zonenum + b"\x00\x0b\x61\x06" + inputnum + b"\x00\xff"
                sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

            # select goto code - used for the goto intent
            # Please note that this command uses a set of input values that are different from
            # those used by setintent
            # You can modify the device names to match your GXR-2 configuration

 
            elif(intent=="goto"):
                if(device=="1" or device=="a.m. FM"):
                    inputnum = b"\x81"
                elif(device=="2" or device=="1 pens music" or device=="music" ):
                    inputnum = b"\x82"
                elif(device=="3" or device=="TV"):
                    inputnum = b"\x83"
                elif(device=="4" or device=="echo"):
                    inputnum = b"\x84"
                elif(device=="5" or device=="glen"):
                    inputnum = b"\x85"
                elif(device=="6" or device=="John"):
                    inputnum = b"\x86"
                else:
                    print("No device found for goto intent")  

                navnum = b"\x2C"
                if(zone=="next" or zone=="next song"):
                    navnum = b"\x2c"
                elif(zone=="previous" or zone=="previous song"):
                    navnum = b"\x2b"

            # Compose and send message to go to next or previous song for a device

                MESSAGE = b"\x00\x0e\x00" + inputnum + b"\x00\x0b\x61\x06" + navnum + b"\x00\xff"
                sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
                        
            # Compose and send message to turn volume up or down   
                
            elif(intent=="adjust"):
                vollevel = device
                if (int(currentlevel) < (int(vollevel) * 10)):
                    delta = (int(vollevel) * 10) - int(currentlevel)
                    MESSAGE = b"\x00\x0e\x00" + zonenum + b"\x00\x0b\x61\x06\x0c\x00\xff"
                elif (int(currentlevel) > (int(vollevel) * 10)):
                    delta = int(currentlevel) - (int(vollevel) * 10)
                    MESSAGE = b"\x00\x0e\x00" + zonenum + b"\x00\x0b\x61\x06\x0d\x00\xff"            
                for x in range (0, delta):
                    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
                    time.sleep(.01)
            sock.close()
       
        else:
            count = count+1
        print(count)
        Date_Time = datetime.datetime.now()
        print(Date_Time)
        input_string = ""
        time.sleep(2)
    
    myMQTTClient.disconnect()
    time.sleep(10)
