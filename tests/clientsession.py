from tp.server.logging import logctx, msg
from tp.server.singleton import SingletonClass
from tp.server.packet import PacketFactory

class ClientSessionHandler( object ):#{{{
	@logctx
	def sessionStarted( self, protocol ):
		self.count = 0
		self.protocol = protocol

		self.scenario = self.scenarioGen()

		self.scenarioStep()

	@logctx
	def packetReceived( self, packet ):
		if packet._name == "Fail":
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
			self.protocol.loseConnection()

	@staticmethod
	def scenarioGen():
		objects = PacketFactory().objects

		yield objects.Connect( 1, "tptests-py client" )
		yield objects.Ping( 2 )
		yield objects.GetFeatures( 3 )
		yield objects.Login( 4, "test@tp", "test" )

		response = yield objects.GetObjectIDs( 5, -1, 0, 0 )
		response = yield objects.GetObjectIDs( 6, -1, 0, response.remaining )
		yield objects.GetObjectsByID( 7, [ id for id, modtime in response.modtimes ] )

		response = yield objects.GetBoardIDs( 10, -1, 0, 0 )
		response = yield objects.GetBoardIDs( 11, -1, 0, response.remaining )
		yield objects.GetBoards( 12, [ id for id, modtime in response.modtimes ] )

		response = yield objects.GetPlayer( 15, [0] )
		#yield objects.Player( 17, [ id for id, modtime in response.modtimes ] )

		yield objects.GetTimeRemaining( 100 )

	def logPrefix( self ):
		return self.__class__.__name__
#}}}
