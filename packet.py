# Code by Graham Northup

import struct
import socket
from io import BytesIO as StringIO

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

        def __bytes__(self):
                return self.buffer.getvalue()

class CMD:
        KEEPALIVE = 0
        MOTION = 1
        SOUND = 2
