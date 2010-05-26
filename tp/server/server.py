from protocol import ThousandParsecProtocol
from logging import logctx, msg
from configuration import ComponentConfiguration, IntegerOption, BooleanOption
from clientsession import ClientSessionHandler

from twisted.internet import reactor, ssl
from twisted.internet.protocol import ServerFactory

from OpenSSL import SSL

class ClientTLSContext( ssl.ClientContextFactory ):
	method = SSL.TLSv1_METHOD

class ThousandParsecServerFactory( ServerFactory, object ):#{{{
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

		from tp.server import db

		dbconfig = "sqlite:///tp.db"
		dbecho = False

		db.setup(dbconfig, dbecho)

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
		self.listeners['tcp'] = reactor.listenTCP( self.__tcp_port_num, self )

		if self.__listen_tls:
			self.listeners['tls'] = reactor.listenSSL( self.__tls_port_num, self, ssl.ClientContextFactory() )

	def logPrefix( self ):
		return self.__class__.__name__
#}}}

class ThousandParsecServerConfiguration( ComponentConfiguration ):#{{{
	component	= ThousandParsecServerFactory

	tcp_port	= IntegerOption( short='p', default=6923, min=1, max=65535,
						help='Specifies number of listening port.', arg_name='PORT' )
	tls_port	= IntegerOption( default=6924, min=1, max=65535,
						help='Specifies number of TLS listening port.', arg_name='PORT' )
	listen_tls	= BooleanOption( short='t', default=False,
						help='Turns on TLS listener.' )
#}}}

