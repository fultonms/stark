import Leap
import time
import socket
import sys
import threading
import struct
from cStringIO import StringIO	
from packet import Packet, CMD

LIN_V = 0.2
ANG_V = 1.0

KA_PKT = Packet()
KA_PKT.write_int(CMD.KEEPALIVE)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ("137.143.51.48", 13698)

def keepAlive():
	sock.sendto(str(KA_PKT), addr)
	threading.Timer(3, keepAlive).start()

def speed(y):
        if (y > 500):
                y = 500
        return((y/500),(y/250))

controller = Leap.Controller()

try:
	keepAlive()
	while True:
		lv = 0
		av =0
		frame = controller.frame()
		hand = frame.hands[0]
		if hand.palm_position.z < -30:
			lv = -1
		elif hand.palm_position.z > 30:
			lv = 1
		elif hand.palm_position.x < -30:
			av = 1
		elif hand.palm_position.x > 30:
			av = -1

		#scales the speed to different values
		#if(hand.palm_position.y > 300):
		#	LIN_V = 1.0
		#	ANG_V = 2.0
		#elif(hand.palm_position.y > 200):
		#	LIN_V = 0.5
		#	ANG_V = 1.0
		#else:
		#	Lin_V  = 0.2
		#	ANG_V = 0.75
		LIN_V,ANG_V = speed(hand.palm_position.y)
		pkt = Packet()
		pkt.write_ubyte(CMD.MOTION)
		pkt.write_double(-LIN_V * lv)
		pkt.write_double(-ANG_V * av)
		sock.sendto(str(pkt), addr)
		time.sleep(1)
except KeyboardInterrupt:
	print("ending")
