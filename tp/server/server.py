from protocol import ThousandParsecProtocol
from logging import logctx, msg
from clientsession import ClientSessionHandler

from twisted.internet import reactor, ssl, error
from twisted.internet.protocol import ServerFactory

from OpenSSL import SSL

class ClientTLSContext( ssl.ClientContextFactory ):
	method = SSL.TLSv1_METHOD

class ThousandParsecServerFactory( ServerFactory, object ):
	protocol = ThousandParsecProtocol
	noisy = False

	@logctx
	def buildProtocol( self, addr ):
		protocol = ServerFactory.buildProtocol( self, addr )
		protocol.SessionHandlerType = ClientSessionHandler

		return protocol

	@logctx
	def doStart(self):
		msg( "Starting factory." )
		ServerFactory.doStart(self)

	@logctx
	def doStop(self):
		msg( "Stopping factory." )
		ServerFactory.doStop(self)

	@logctx
	def clientConnectionFailed(self, connector, reason):
		msg( "Connection failed: %s" % reason.getErrorMessage() )

	@logctx
	def clientConnectionLost(self, connector, reason):
		msg( "Connection lost: %s" % reason.getErrorMessage() )

	def configure( self, configuration ):
		self.__tcp_port_num	= configuration.tcp_port
		self.__tls_port_num	= configuration.tls_port
		self.__listen_tls	= configuration.listen_tls

		self.listeners = dict( tcp=None, tls=None )

	def start( self ):
		reactor.callLater( 0, self.__startListening )
	
	@logctx
	def __startListening( self ):
		try:
			port = reactor.listenTCP( self.__tcp_port_num, self )
		except error.CannotListenError, ex:
			msg( "${red1}Cannot open listening port on %d: %s.${coff}" % (ex.port, ex.socketError[1]), level='error' )
		else:
			self.listeners['tcp'] = port

		if self.__listen_tls:
			try:
				port = reactor.listenSSL( self.__tls_port_num, self, ssl.ClientContextFactory() )
			except error.CannotListenError, ex:
				msg( "${red1}Cannot open listening port on %d: %s.${coff}" % (ex.port, ex.socketError[1]), level='error' )
			else:
				self.listeners['tls'] = port

		if all( port == None for proto, port in self.listeners.items() ):
			msg( "${red1}No listening ports. Quitting...${coff}", level='error' )
			reactor.stop()

	def logPrefix( self ):
		return self.__class__.__name__

__all__ = [ 'ThousandParsecServerFactory' ]
