from tp.server.logging import logctx, msg
from tp.server.singleton import SingletonClass
from tp.server.packet import PacketFactory

class ClientSessionHandler( object ):#{{{
	@logctx
	def sessionStarted( self, protocol ):
		self.count = 0
		self.protocol = protocol

		self._scenario = self.protocol.factory.scenario
		self.scenario = self.protocol.factory.scenario.__iter__()

		self.scenarioStep()

	@logctx
	def packetReceived( self, packet ):
		if packet._name == "Fail":
			self._scenario.status = False
			self.protocol.loseConnection()
		elif packet._name == "Sequence":
			self.count = packet.number - 1
		elif self.count > 0:
			self.count -= 1
		else:
			self.scenarioStep( packet )

	@logctx
	def connectionLost( self, reason ):
		pass
	
	@logctx
	def scenarioStep( self, packet = None ):
		try:
			self.protocol.sendPacket( self.scenario.send( packet ) )
		except StopIteration, ex:
			self._scenario.status = True
			self.protocol.loseConnection()
	
	def logPrefix( self ):
		return self.__class__.__name__
#}}}
