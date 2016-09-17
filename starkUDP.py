import Leap, time
controller = Leap.Controller()

try:
	while True:
		frame = controller.frame()
		hand = frame.hands[0]
		if hand.palm_position.z < -30:
			print "forward"
		elif hand.palm_position.z > 40:
			print "backward"
		elif hand.palm_position.x < -30:
			print "turning left"
		elif hand.palm_position.x > 30:
			print "turning right"
		else:
			print "stopped"
		print str(hand.palm_position.y) + " is speed"
except KeyboardInterrupt:
	print "ending"
