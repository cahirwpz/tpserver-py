import struct

from logging import *

from twisted.internet.protocol import Protocol

from tp.server.logger import logctx
from tp.server.packet import PacketFactory, PacketFormatter

class ThousandParsecProtocol( Protocol, object ):
	SessionHandlerType = None

	@logctx
	def connectionMade( self ):
		debug( "Connection established with %s:%d", self.transport.getPeer().host, self.transport.getPeer().port) 

		self.loseConnection = self.transport.loseConnection

		try:
			if self.SessionHandlerType:
				self.handler = self.SessionHandlerType()
		except Exception, ex:
			exception( "Exception %s(%s) caught!" % (ex.__class__.__name__, str(ex)) )
			self.handler = None
			self.transport.loseConnection()
		
		if self.handler is not None:
			self.handler.sessionStarted( self )

		self.__header = None
		self.__buffer = ""

	@logctx
	def dataReceived( self, data ):
		self.__buffer += data

		while len( self.__buffer ) >= 16:
			if not self.__header:
				if len( self.__buffer ) >= 16:
					self.__header = struct.unpack('!4sLLL', self.__buffer[:16] )

					version, sequence, command, length = self.__header

					if version not in PacketFactory():
						self.sendPacket( PacketFactory()['default']['Fail']( 0, "Protocol %s not supported" % version ) )
						self.loseConnection()

					if length > 2**20:
						self.sendPacket( PacketFactory()['default']['Fail']( 0, "Payload is too long (%d bytes)" % length ) )
						self.loseConnection()

			if self.__header:
				version, sequence, command, length = self.__header

				packetSize = length + 16

				if len( self.__buffer ) >= packetSize:
					binary = self.__buffer[:packetSize]

					debug( "Received binary: %s", binary.encode("hex") )

					packet = PacketFactory().fromBinary( version, command, binary )

					if packet:
						debug( "Received %s:\n%s", packet._base.lower(), PacketFormatter(packet) ) 

						self.handler.packetReceived( packet )
					else:
						self.loseConnection()

					self.__header = None
					self.__buffer = self.__buffer[packetSize:]

	@logctx
	def connectionLost( self, reason ):
		debug( "Connection was lost: %s", reason.value )

		if self.handler is not None:
			self.handler.connectionLost( reason )

	@logctx
	def sendPacket( self, packet ):
		binary = packet.pack()

		debug( "Sending %s:\n%s", packet._base.lower(), PacketFormatter(packet) ) 
		debug( "Sending binary: %s", binary.encode("hex") )

		self.transport.write( binary )

	def logPrefix( self ):
		return self.__class__.__name__

__all__ = [ 'ThousandParsecProtocol' ]
