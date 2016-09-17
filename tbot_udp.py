#Code by Graham Northup

import socket
import struct
import time
from cStringIO import StringIO

import rospy
from geometry_msgs.msg import Twist
from kobuki_msgs.msg import BumperEvent, Sound

##### Configuration #####

# Address to listen to (empty indicates all interfaces)
LISTEN_ADDR=''
LISTEN_PORT=13676

# Cut power if we lose keepalives
TERM_ON_KA=True
KA_TIMEOUT = 3  # seconds

# Rate with which to publish commands (also controls responsiveness)
CMD_RATE = 10

# Don't set linear velocity if the bumper is detected
DONT_BUMP=True
BUMP_REV_SPEED = 0.05  # This MUST be positive
BUMP_REV_TIME = 1.5

##### Protocol #####

class Packet(object):
	def __init__(self, ival = None):
		if ival is not None:
			self.buffer = StringIO(ival)
		else:
			self.buffer = StringIO()

	# Staticmethod
	def _reader(fmt):
		return lambda self: struct.unpack(fmt, self.buffer.read(struct.calcsize(fmt)))[0]

	# Staticmethod
	def _writer(fmt):
		return lambda self, obj: self.buffer.write(struct.pack(fmt, obj))

	read_byte = _reader('!b')
	read_ubyte = _reader('!B')
	read_short = _reader('!h')
	read_ushort = _reader('!H')
	read_int = _reader('!i')
	read_uint = _reader('!I')
	read_long = _reader('!l')
	read_ulong = _reader('!L')
	read_float = _reader('!f')
	read_double = _reader('!d')

	write_byte = _writer('!b')
	write_ubyte = _writer('!B')
	write_short = _writer('!h')
	write_ushort = _writer('!H')
	write_int = _writer('!i')
	write_uint = _writer('!I')
	write_long = _writer('!l')
	write_ulong = _writer('!L')
	write_float = _writer('!f')
	write_double = _writer('!d')

	def __str__(self):
		return self.buffer.getvalue()

class CMD:
	KEEPALIVE = 0
	MOTION = 1
	SOUND = 2

class Processor(object):
	dispatch = {}
	motion = Twist()
	lastka = None
	impact = [False]*3
	backingsince = None

	def __init__(self, addr):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.bind(addr)
		self.socket.setblocking(False)
		print 'Listener ready on', addr

	def tick(self):
		try:
			while True:
				data, src = self.socket.recvfrom(4096)
				self.src = src
				self.process_pkt(Packet(data))
		except socket.error:
			pass
		if self.lastka is not None and time.time() > self.lastka + KA_TIMEOUT:
			print 'KA timeout'
			self.lastka = None
			if TERM_ON_KA:
				print '(killing motors)'
				self.motion.linear.x = 0
				self.motion.angular.z = 0

	def process_pkt(self, pkt):
		self.cmd = pkt.read_ubyte()
		self.dispatch.get(self.cmd, self.no_cmd)(self, pkt)

	def no_cmd(self, _, pkt):
		print 'Warning: unknown command:', self.cmd

	def on_bump(self, status):
		self.impact[status.bumper] = bool(status.state)

	def get_motion(self):
		t = Twist()
		buf = StringIO()
		self.motion.serialize(buf)
		t.deserialize(buf.getvalue())
		if DONT_BUMP:
			if any(self.impact):
				self.backingsince = time.time()
				self.motion.linear.x = 0
			if self.backingsince is not None:
				if time.time() < self.backingsince + BUMP_REV_TIME:
					t.linear.x = -BUMP_REV_SPEED
				else:
					self.backingsince = None
		return t

	@classmethod
	def _dispatch(cls, cmd):
		def _inner(f):
			cls.dispatch[cmd] = f
			return f
		return _inner

@Processor._dispatch(CMD.KEEPALIVE)
def proc_cmd_keepalive(self, pkt):
	if self.lastka is None:
		print 'New KA from', self.src
	self.lastka = time.time()

@Processor._dispatch(CMD.MOTION)
def proc_cmd_motion(self, pkt):
	self.motion.linear.x = pkt.read_double()
	self.motion.angular.z = pkt.read_double()
	print self.src, ':', 'motion', self.motion.linear.x, self.motion.angular.z

sound_node = None
@Processor._dispatch(CMD.SOUND)
def proc_cmd_sound(self, pkt):
	snd = pkt.read_ubyte()
	print 'Sound:', snd
	sound_node.publish(Sound(snd))

if __name__ == '__main__':
	proc = Processor((LISTEN_ADDR, LISTEN_PORT))
	rospy.init_node('tbot', anonymous=False)
	motion_node = rospy.Publisher('mobile_base/commands/velocity', Twist, queue_size=10)
	rospy.Subscriber('mobile_base/events/bumper', BumperEvent, proc.on_bump)
	sound_node = rospy.Publisher('mobile_base/commands/sound', Sound, queue_size=10)
	rate = rospy.Rate(CMD_RATE)
	rospy.on_shutdown(lambda: motion_node.publish(Twist()))
	while not rospy.is_shutdown():
		proc.tick()
		motion_node.publish(proc.get_motion())
		rate.sleep()
