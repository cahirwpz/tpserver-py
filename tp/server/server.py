#!/usr/bin/env python

from logging import debug, error

from tp.server.protocol import ThousandParsecProtocol
from tp.server.clientsession import ClientSessionHandler

from twisted.internet import reactor, ssl
from twisted.internet.error import CannotListenError
from twisted.internet.protocol import ServerFactory

from OpenSSL import SSL

class ClientTLSContext( ssl.ClientContextFactory ):
	method = SSL.TLSv1_METHOD

class ThousandParsecServerFactory( ServerFactory, object ):
	protocol = ThousandParsecProtocol
	noisy = False

	def buildProtocol( self, addr ):
		protocol = ServerFactory.buildProtocol( self, addr )
		protocol.SessionHandlerType = ClientSessionHandler

		return protocol

	def doStart(self):
		debug( "Starting factory." )
		ServerFactory.doStart(self)

	def doStop(self):
		debug( "Stopping factory." )
		ServerFactory.doStop(self)

	def clientConnectionFailed(self, connector, reason):
		debug( "Connection failed: %s", reason.getErrorMessage() )

	def clientConnectionLost(self, connector, reason):
		debug( "Connection lost: %s", reason.getErrorMessage() )

	def configure( self, configuration ):
		self.__tcp_port_num	= configuration.tcp_port
		self.__tls_port_num	= configuration.tls_port
		self.__listen_tls	= configuration.listen_tls

		self.listeners = dict( tcp=None, tls=None )

	def start( self ):
		reactor.callLater( 0, self.__startListening )
	
	def __startListening( self ):
		try:
			port = reactor.listenTCP( self.__tcp_port_num, self )
		except CannotListenError, ex:
			error( "Cannot open listening port on %d: %s.", ex.port, ex.socketError[1]) 
		else:
			self.listeners['tcp'] = port

		if self.__listen_tls:
			try:
				port = reactor.listenSSL( self.__tls_port_num, self, ssl.ClientContextFactory() )
			except CannotListenError, ex:
				error( "Cannot open listening port on %d: %s.", ex.port, ex.socketError[1]) 
			else:
				self.listeners['tls'] = port

		if all( port == None for proto, port in self.listeners.items() ):
			error( "No listening ports. Quitting..." )
			reactor.stop()

__all__ = [ 'ThousandParsecServerFactory' ]
