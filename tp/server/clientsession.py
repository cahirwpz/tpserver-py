#!/usr/bin/env python

import inspect
from logging import debug, error, exception

from collections import Mapping

from tp.server.model import Player
from tp.server.gamemanager import Game
from tp.server.singleton import SingletonContainerClass
from tp.server.packet import PacketFactory

import tp.server.commands

class CommandDispatcher( Mapping ):
	__metaclass__ = SingletonContainerClass

	def __init__( self ):
		self.__commands = {}

		for name, cls in inspect.getmembers( tp.server.commands, lambda o: inspect.isclass(o) ):
			debug( "Loaded %s command handler.", cls.__name__ )

			self.__commands[ name ] = cls
		
	def __getitem__( self, name ):
		return self.__commands[ name ]

	def __iter__( self ):
		return self.__commands.__iter__()

	def __len__( self ):
		return self.__commands.__len__()

class ClientSessionContext( object ):
	def __init__( self ):
		self.__game   = None
		self.__player = None

	@property
	def player( self ):
		return self.__player

	@player.setter
	def player( self, value ):
		if isinstance( value, Player ):
			self.__player = value
		else:
			raise TypeError( "Player value must either be a Player object!" )

	@property
	def game( self ):
		return self.__game

	@game.setter
	def game( self, value ):
		if isinstance( value, Game ):
			self.__game = value
		else:
			raise TypeError( "Player value must either be a Game object!" )

class ClientSessionHandler( object ):
	def __init__( self ):
		self.__packets = None
		self.__context = ClientSessionContext()
		
		self.lastSeq = None

	def sessionStarted( self, protocol ):
		self.protocol = protocol

	def packetReceived( self, packet ):
		debug( "Going to deal with %s packet.", packet.__class__.__name__ )

		if not self.__packets:
			self.__packets = PacketFactory()[ packet._version ]

		Fail = self.__packets.use( 'Fail' )

		if self.lastSeq != None and self.lastSeq >= packet._sequence:
			response = Fail( packet._sequence, "Frame", "Wrong sequence number!", [] )
		else:
			self.lastSeq = packet._sequence

			try:
				handler = CommandDispatcher()[ packet.__class__.__name__ ]( self.__packets, self.__context )
			except KeyError:
				error( "No handler for %s command!", packet._name )

				response = Fail( packet._sequence, "UnavailablePermanently", "Command '%s' not supported!" % packet._name )
			else:
				debug( "Calling %s handler method.", handler.__class__.__name__ )

				try:
					response = handler( packet )
				except Exception as ex:
					exception( "Handler for command %s failed:\n%s", packet.__class__.__name__, ex )
					response = None
				
				if not response:
					response = Fail( packet._sequence, "UnavailablePermanently", "Internal server error!", [])

		self.sendResponse( response )

	def sendResponse( self, response ):
		if isinstance( response, list ):
			for r in response:
				self.protocol.sendPacket( r )
		else:
			self.protocol.sendPacket( response )

	def connectionLost( self, reason ):
		pass

__all__ = [ 'ClientSessionContext', 'ClientSessionHandler' ]
