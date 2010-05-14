from tp.server.protocol import ThousandParsecProtocol
from tp.server.logging import logctx, msg

from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory

from clientsession import ClientSessionHandler

class ThousandParsecClientFactory( ClientFactory, object ):#{{{
	protocol = ThousandParsecProtocol
	noisy = False

	@logctx
	def buildProtocol( self, addr ):
		protocol = ClientFactory.buildProtocol( self, addr )
		protocol.SessionHandlerType = ClientSessionHandler

		return protocol

	@logctx
	def doStart(self):
		msg( "Starting factory." )
		ClientFactory.doStart(self)

	@logctx
	def doStop(self):
		msg( "Stopping factory." )
		ClientFactory.doStop(self)

		try:
			self.finished
		except AttributeError:
			pass
		else:
			reactor.callLater( 0, self.finished, self.scenario.status )

	@logctx
	def clientConnectionFailed(self, connector, reason):
		msg( "Connection failed: %s" % reason.getErrorMessage() )

	@logctx
	def clientConnectionLost(self, connector, reason):
		msg( "Connection lost: %s" % reason.getErrorMessage() )

	def logPrefix( self ):
		return self.__class__.__name__
#}}}
