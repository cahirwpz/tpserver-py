from tp.server.protocol import ThousandParsecProtocol
from tp.server.logging import logctx, msg

from twisted.internet.protocol import ClientFactory

class ThousandParsecClientFactory( ClientFactory, object ):#{{{
	protocol = ThousandParsecProtocol
	noisy = False

	@logctx
	def buildProtocol( self, addr ):
		return ClientFactory.buildProtocol( self, addr )

	@logctx
	def doStart(self):
		msg( "Starting factory." )
		ClientFactory.doStart(self)

	@logctx
	def doStop(self):
		msg( "Stopping factory." )
		ClientFactory.doStop(self)

	@logctx
	def clientConnectionFailed( self, connector, reason ):
		msg( "Connection failed: %s" % reason.getErrorMessage() )

	@logctx
	def clientConnectionLost( self, connector, reason ):
		msg( "Connection lost: %s" % reason.getErrorMessage() )

	def logPrefix( self ):
		return self.__class__.__name__
#}}}

__all__ = [ 'ThousandParsecClientFactory' ]
