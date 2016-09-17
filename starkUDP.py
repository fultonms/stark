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
		
		if av != 0 or lv != 0:	
			pkt = Packet()
			pkt.write_ubyte(CMD.MOTION)
			pkt.write_double(-LIN_V * lv)
			pkt.write_double(-ANG_V * av)
			sock.sendto(str(pkt), addr)
			time.sleep(1)
except KeyboardInterrupt:
	print("ending")
