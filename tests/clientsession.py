from twisted.internet import reactor

from tp.server.packet import PacketFactory
from tp.server.logging import logctx, msg

class ClientSessionHandler( object ):#{{{
	status   = False
	finished = None

	@logctx
	def sessionStarted( self, transport ):
		self.transport = transport

	@logctx
	def packetReceived( self, packet ):
		pass

	@logctx
	def connectionLost( self, reason ):
		msg( "Disconnected.", level="info" )

		if self.finished != None:
			reactor.callLater( 0, self.finished, self )
	
	def logPrefix( self ):
		return self.__class__.__name__
#}}}

def ichain( *args ):#{{{
	for a in args:
		try:
			r = None
			while True:
				r = yield a.send(r)
		except StopIteration:
			pass
#}}}

class IncrementingSequenceMixin( object ):#{{{
	@property
	def seq( self ):
		try:
			self.__seq += 1
		except AttributeError:
			self.__seq = 1
		
		return self.__seq
#}}}

class TestSession( ClientSessionHandler ):#{{{
	NoFailAllowed = True

	def __init__( self ):
		self.count  = 0
		self.status = True
		self.protocol = PacketFactory().objects
		self.scenarioList = []

		self.failRequest  = None
		self.failResponse = None
	
	@logctx
	def sessionStarted( self, transport ):
		super( TestSession, self ).sessionStarted( transport )

		msg( "Connection established.", level="info" )

		self.scenarioList.append( self.__iter__() )

		self.scenario = ichain( *self.scenarioList )
		self.step()

	@logctx
	def packetReceived( self, packet ):
		msg( "Received ${cyn1}%s${coff} packet." % packet._name, level="info" )

		if self.NoFailAllowed and packet._name == "Fail":
			self.status = False
			self.reason = "Fail packet received!"
			self.failResponse = packet
			self.transport.loseConnection()
		elif packet._name == "Sequence":
			self.count = packet.number - 1
		elif self.count > 0:
			self.count -= 1
		else:
			self.step( packet )

	def step( self, response = None ):
		try:
			request = self.scenario.send( response )
		except StopIteration, ex:
			self.transport.loseConnection()
		else:
			self.transport.sendPacket( request )
			self.failRequest = request

			if request != None:
				msg( "Sending ${cyn1}%s${coff} packet." % request._name, level="info" )
#}}}
