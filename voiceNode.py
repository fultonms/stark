import speech_recognition as sr
import time
import socket
import sys
import threading
import struct
from random import randint
from packet import Packet, CMD

botIp = {} #used as a dictionary for botIps
botIp['donatello']  =  ("137.143.52.234", 13676)
botIp['raphael'] =  ("137.143.63.255", 13698)

cmd_buffer = list()

LIN_V = 0.2
ANG_V = 1

KA_PKT = Packet()
KA_PKT.write_ubyte(CMD.KEEPALIVE)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# obtain audio from the microphone
r = sr.Recognizer()
m = sr.Microphone()

def keepAlive():
    for key in botIp:
        sock.sendto(str(KA_PKT), botIp[key])
    threading.Timer(3, keepAlive).start()

def controlLoop(ip):
    global LIN_V, ANG_V
    word = None
    while('end' != word and 'exit' != word):
        if len(cmd_buffer)> 0 : 
            word = cmd_buffer.pop(0)
            print word
            lv = 0
            av = 0
            if('forward' == word or 'charge' == word):
                lv = LIN_V * 1
            elif('backward' == word or 'reverse' == word):
                lv = LIN_V * -1
            elif('right' == word):
                av = ANG_V * -1
            elif('left' == word):
                av = ANG_V * 1
            elif('faster' == word):
                LIN_V += 0.2
                ANG_V += 0.2
                print LIN_V, ANG_V
            elif('slower' == word):
                LIN_V = LIN_V - 0.2    
                ANG_V = ANG_V - 0.2
                print LIN_V, ANG_V
            elif('stop' == word):
                lv = 0
                av = 0
            elif('sing' == word):
                pkt = Packet()
                pkt.write_ubyte(CMD.SOUND)
                val = randint(0, 6)
                pkt.write_ubyte(val)
                sock.sendto(str(pkt), ip)
                
            else:
                pass
            
            pkt = Packet()
            pkt.write_ubyte(CMD.MOTION)
            pkt.write_double(lv)
            pkt.write_double(av)
            sock.sendto(str(pkt), ip)
            
    print('leaving control loop')


def callback(recognizer, audio):
    global cmd_buffer
    try:
        words = recognizer.recognize_google(audio).split()
        cmd_buffer.extend([str(item.lower()) for item in words])
    except sr.UnknownValueError:
            print ("Didn't catch that")
    except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))

keepAlive()
try:
    print("Quiet please!")
    with m as source: r.adjust_for_ambient_noise(source)
    print("Ambient levels detected.")
    stop_listening = r.listen_in_background(m, callback)
    while True:
        try:
            if len(cmd_buffer)> 0 : 
                word = cmd_buffer.pop(0)
                if(word == 'donatello' or word == 'raphael'):
                    print('dropping into {0}\'s control'.format(word))
                    controlLoop(botIp[word])
            time.sleep(0.1)
        except sr.UnknownValueError:
            print ("Didn't catch that")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
            
except KeyboardInterrupt:
    stop_listening()
    pass            
