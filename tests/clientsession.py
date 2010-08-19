#!/usr/bin/env python

from logging import debug
from twisted.internet import reactor

class ClientSessionHandler( object ):
	status   = False
	finished = None

	def sessionStarted( self, transport ):
		self.transport = transport

	def packetReceived( self, packet ):
		pass

	def connectionLost( self, reason ):
		debug( "Disconnected." )

		if self.finished != None:
			reactor.callLater( 0, self.finished, self )

__all__ = [ 'ClientSessionHandler' ]
