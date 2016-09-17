import Leap
import time
import socket
import sys
import threading

from packet import Packet, CMD
from site import addusersitepackages

LIN_V = 0.2
ANG_V = 1.0

KA_PKT = Packet()
KA_PKT.write_ubyte(CMD.KEEPALIVE)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ("137.143.51.48", 13698)

def keepAlive():
	sock.sendto(bytes(KA_PKT), addr)
	threading.Timer(100, keepAlive).start()


controller = Leap.Controller()

try:
	#keepAlive()
	while True:
		lv = 0
		av =0
		frame = controller.frame()
		hand = frame.hands[0]
		if hand.palm_position.z < -30:
			lv = 1
		elif hand.palm_position.z > 40:
			lv = -1
		elif hand.palm_position.x < -30:
			av = 1
		elif hand.palm_position.x > 30:
			av = -1
		
		if av != 0 or lv != 0:	
			pkt = Packet()
			pkt.write_ubyte(CMD.MOTION)
			pkt.write_double(-LIN_V * lv)
			pkt.write_double(-ANG_V * av)
			sock.sendto(bytes(pkt), addr)
			time.sleep(1)
except KeyboardInterrupt:
	print "ending"
