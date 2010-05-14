from twisted.internet import reactor

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
