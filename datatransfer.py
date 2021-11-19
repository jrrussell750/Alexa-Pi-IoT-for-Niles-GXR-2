import time
import json
import socket
import logging
import os
import re
from array import *
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

myMQTTClient = AWSIoTMQTTClient("NilesPiClientID") #random key, if another connection using the same key is opened the previous one is auto closed by AWS IOT
myMQTTClient.configureEndpoint("a3ci7g5ta9i6w4-ats.iot.us-west-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/pi/AWSIoT/AmazonRootCA1.pem", "/home/pi/AWSIoT/private.pem.key", "/home/pi/AWSIoT/certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2) # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10) # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5) # 5 sec

input_string = ""
zonenum = b"\x00"
inputnum = b"\x00"
count = 0

def customCallback(self, params, packet):
    global input_string
    input_string = packet.payload

print ('Initiating IoT Core Topic ...')
myMQTTClient.connect()

while (1):    
    myMQTTClient.subscribe("niles/gxr2", 1, customCallback)
    string_length = len(input_string)
    if (string_length > 0):
        count = 0
        intent = ""
        zone = ""
        device = ""
        index = 1

        # parse input string

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
        
        #select zone and device codes
 
        if(intent=="set"):
            zonenum = b"\x24"
            if(zone=="zone 1" or zone=="living room"):
                zonenum = b"\x21"
            elif(zone=="zone 2" or zone=="kitchen"):
                zonenum = b"\x22"
            elif(zone=="zone 3"):
                zonenum = b"\x23"
            elif(zone=="zone 4" or zone=="patio"):
                zonenum = b"\x24"
            elif(zone=="zone 5" or zone=="master bath"):
                zonenum = b"\x25"
            elif(zone=="zone 6" or zone=="basement"):
                zonenum = b"\x26"
            else:
                print("No zone found")

  
            inputnum = b"\x04"    
            if(device=="input 1" or device=="a.m. FM"):
                inputnum = b"\x01"
            elif(device=="input 2" or device=="1 pens music" or device=="music" ):
                inputnum = b"\x02"
            elif(device=="input 3" or device=="TV"):
                inputnum = b"\x03"
            elif(device=="input 4" or device=="echo"):
                inputnum = b"\x04"
            elif(device=="input 5" or device=="glen"):
                inputnum = b"\x05"
            elif(device=="input 6" or device=="John"):
                inputnum = b"\x06"
            elif(device=="off"):
                inputnum = b"\x0a"
            else:
                print("No device found")  
        
            MESSAGE = b"\x00\x0e\x00" + zonenum + b"\x00\x0b\x61\x06" + inputnum + b"\x00\xff"
            UDP_IP = "10.100.0.1"
            UDP_PORT = 6001
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
            sock.close()
            print (intent + " " + zone + " " + device)
            
        elif(intent=="volume"):
            zonenum = b"\x24"
            statusfile = open("GXR2status.txt", "r")
            statusarray = ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]  
            for i in range (0,12):
                statusarray[i] = statusfile.readline()
                print(statusarray[i])
            statusfile.close() 
    
            if(zone=="zone 1" or zone=="living room"):
                zonenum = b"\x21"
                i = 6
            elif(zone=="zone 2" or zone=="kitchen"):
                zonenum = b"\x22"
                i = 7
            elif(zone=="zone 3" or zone=="master bedroom"):
                zonenum = b"\x23"
                i = 8
            elif(zone=="zone 4" or zone=="patio"):
                zonenum = b"\x24"
                i = 9
            elif(zone=="zone 5" or zone=="master bath"):
                zonenum = b"\x25"
                i = 10
            elif(zone=="zone 6" or zone=="basement"):
                zonenum = b"\x26"
                i = 11
            currentlevel = statusarray[i]
            UDP_IP = "10.100.0.1"
            UDP_PORT = 6001
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if (int(currentlevel) > (int(vollevel) * 10)):
                delta = int(currentlevel) - (int(vollevel) * 10)
                MESSAGE = b"\x00\x0e\x00" + zonenum + b"\x00\x0b\x61\x06\x0d\x00\xff"
                for x in range(0, delta):
                    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
                    time.sleep(.01)
            else:
                delta = (int(vollevel) * 10) - int(currentlevel)
                MESSAGE = b"\x00\x0e\x00" + zonenum + b"\x00\x0b\x61\x06\x0c\x00\xff"
                for x in range (0, delta):
                    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
                    time.sleep(.01)
            sock.close()
    else:
        count = count+1
    input_string = ""
    if (count < 1000):
        time.sleep(2)
    else:
        time.sleep(5)
        
