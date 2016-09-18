import speech_recognition as sr
from test import audiotests
import socket
import sys
import threading
import struct
from cStringIO import StringIO	
from packet import Packet, CMD

botIp = {} #used as a dictionary for botIps
botIp['lou']  =  ("137.143.63.255", 13698)
botIp['raphael'] =  ("137.143.63.255", 13698)

KA_PKT = Packet()
KA_PKT.write_int(CMD.KEEPALIVE)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# obtain audio from the microphone
r = sr.Recognizer()
m = sr.Microphone()

def keepAlive():
    sock.sendto(str(KA_PKT), botIp['lou'])
    threading.Timer(3, keepAlive).start()


def findSpeed(words):
    if('one' in words):
        return(.2)
    elif('three' in words):
        return(1)
    else:
        return(.5)

def control(words,ip):
    name = words[0]
    print('droping into {0}\'s control'.format(name))
    while('end' not in words):
        lspeed = 0
        aspeed = 0
        if('forward' in words):
            lspeed = findSpeed(words)
        elif('backward' in words):
            lspeed = findSpeed(words) * -1
        elif('right' in words):
            aspeed = findSpeed(words) * 2
        elif('left' in words):
            aspeed = findSpeed(words) * -2
        print('linear: ' + str(lspeed) + " rotational: " + str(aspeed))
        pkt = Packet()
        pkt.write_ubyte(CMD.MOTION)
        pkt.write_double(lspeed)
        pkt.write_double(aspeed)
        sock.sendto(str(pkt), ip)
        print("Listening...")
        #with m as source: audio = r.listen(source)
        try:
            print"Recognizing..."
            #command = r.recognize_sphinx(audio)
            command = raw_input('debugging : ')
            print("You said: {0}".format(command))
            words = command.split(' ')
        except sr.UnknownValueError:
            print ("Didn't catch that")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
    print('leaving {0}\'s control'.format(name))




keepAlive()
try:
    print("Quiet please!")
    with m as source: r.adjust_for_ambient_noise(source)
    print("Ambient levels detected.")
    while True:
        print("Listening...")
        #with m as source: audio = r.listen(source)
        try:
            print"Recognizing..."
            #command = r.recognize_sphinx(audio)
            command = raw_input('deubugging: ')
            print("You said: {0}".format(command))
            words = command.split(' ')
            if(words[0] == 'lou' or words[0] == 'raphael'):
                control(words,botIp[words[0]])
            
        except sr.UnknownValueError:
            print ("Didn't catch that")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
            
except KeyboardInterrupt:
    pass            
