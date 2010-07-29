import struct

from twisted.internet.protocol import Protocol

from logging import logctx, msg, err
from packet import PacketFactory, PacketFormatter

class ThousandParsecProtocol( Protocol, object ):#{{{
	SessionHandlerType = None

	@logctx
	def connectionMade( self ):
		msg( "${grn1}Connection established with %s:%d${coff}" % (self.transport.getPeer().host, self.transport.getPeer().port) )

		self.loseConnection = self.transport.loseConnection

		try:
			self.handler = self.SessionHandlerType()
		except Exception, ex:
			err()
			self.handler = None
			self.transport.loseConnection()
		
		if self.handler:
			self.handler.sessionStarted( self )

		self.header = None
		self.buffer = ""

	@logctx
	def dataReceived( self, data ):
		self.buffer += data

		while len( self.buffer ) >= 16:
			if not self.header:
				if len( self.buffer ) >= 16:
					self.header = struct.unpack('!4sLLL', self.buffer[:16] )

					version, sequence, command, length = self.header

					if version not in PacketFactory():
						self.sendPacket( PacketFactory()['default']['Fail']( 0, "Protocol %s not supported" % version ) )
						self.loseConnection()

					if length > 2**20:
						self.sendPacket( PacketFactory()['default']['Fail']( 0, "Payload is too long (%d bytes)" % length ) )
						self.loseConnection()

			if self.header:
				version, sequence, command, length = self.header

				packetSize = length + 16

				if len( self.buffer ) >= packetSize:
					binary = self.buffer[:packetSize]

					msg( "Received binary: %s" % binary.encode("hex"), level='debug2' )

					packet = PacketFactory().fromBinary( version, command, binary )

					if packet:
						msg( "${cyn1}Received %s:${coff}\n%s" % ( packet._base.lower(), PacketFormatter(packet) ) )

						self.handler.packetReceived( packet )
					else:
						self.loseConnection()

					self.header = None
					self.buffer = self.buffer[packetSize:]

	@logctx
	def connectionLost( self, reason ):
		msg( "${red1}Connection was lost: %s${coff}" % reason.value )

		if self.handler:
			self.handler.connectionLost( reason )

	@logctx
	def sendPacket( self, packet ):
		binary = packet.pack()

		msg( "${cyn1}Sending %s:${coff}\n%s" % ( packet._base.lower(), PacketFormatter(packet) ) )
		msg( "Sending binary: %s" % binary.encode("hex"), level='debug2' )

		self.transport.write( binary )

	def logPrefix( self ):
		return self.__class__.__name__
#}}}

__all__ = [ 'ThousandParsecProtocol' ]
