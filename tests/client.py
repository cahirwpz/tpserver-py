#!/usr/bin/env python

from logging import debug
from OpenSSL import SSL

from configuration import ComponentConfiguration, StringOption, IntegerOption, BooleanOption

from tp.server.protocol import ThousandParsecProtocol
from tp.server.singleton import SingletonClass

from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor, ssl

class ClientTLSContext( ssl.ClientContextFactory ):
	method = SSL.TLSv1_METHOD

class ThousandParsecClientFactory( ClientFactory, object ):
	__metaclass__ = SingletonClass

	protocol = ThousandParsecProtocol
	noisy = False

	def __init__( self ):
		self.__tests = []

	def makeTestSession( self, test ):
		self.__tests.append( test )

		if self.__use_tls:
			reactor.connectSSL( self.__hostname, self.__tls_port_num, self, ClientTLSContext() )
		else:
			reactor.connectTCP( self.__hostname, self.__tcp_port_num, self )

	def buildProtocol( self, addr ):
		protocol = ClientFactory.buildProtocol( self, addr )
		protocol.handler = self.__tests.pop(0)

		return protocol

	def doStart(self):
		debug( "Starting factory." )
		ClientFactory.doStart(self)

	def doStop(self):
		debug( "Stopping factory." )
		ClientFactory.doStop(self)

	def clientConnectionFailed( self, connector, reason ):
		debug( "Connection failed: %s", reason.getErrorMessage() )

	def clientConnectionLost( self, connector, reason ):
		debug( "Connection lost: %s", reason.getErrorMessage() )

	def configure( self, configuration ):
		self.__hostname = configuration.hostname
		self.__tcp_port_num = configuration.tcp_port
		self.__tls_port_num = configuration.tls_port
		self.__use_tls = configuration.use_tls

class ThousandParsecClientFactoryConfiguration( ComponentConfiguration ):
	component = ThousandParsecClientFactory

	hostname	= StringOption( short='H', default='localhost',
								help='Specifies server hostname.', arg_name='FQDN' )
	tcp_port	= IntegerOption( short='p', default=6923, min=1, max=65535,
								help='Specifies server port.', arg_name='PORT' )
	tls_port	= IntegerOption( default=6924, min=1, max=65535,
								help='Specifies TLS server port.', arg_name='PORT' )
	use_tls		= BooleanOption( short='T', default=False,
								help='Use TLS instead of TCP connection.' )

__all__ = [ 'ThousandParsecClientFactory', 'ThousandParsecClientFactoryConfiguration' ]
