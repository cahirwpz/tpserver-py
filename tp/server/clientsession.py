from logging import logctx, msg, err

from tp.server.bases import Game, Player
from cmdhandler import CommandDispatcher

from packet import PacketFactory

class ClientSessionContext( object ):#{{{
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
#}}}

class ClientSessionHandler( object ):#{{{
	def __init__( self ):
		self.__packets = None
		self.__context = ClientSessionContext()
		
		self.lastSeq = None

	@logctx
	def sessionStarted( self, protocol ):
		self.protocol = protocol

	@logctx
	def packetReceived( self, packet ):
		msg( "${wht1}Going to deal with ${mgt1}%s${wht1} packet.${coff}" % packet._name )

		if not self.__packets:
			self.__packets = PacketFactory()[ packet._version ]

		Fail = self.__packets.use( 'Fail' )

		if self.lastSeq != None and self.lastSeq >= packet._sequence:
			response = Fail( packet._sequence, "Frame", "Wrong sequence number!", [] )
		else:
			self.lastSeq = packet._sequence

			try:
				handler = CommandDispatcher()[ packet._name ]( self.__packets, self.__context )
			except KeyError:
				msg( "${red1}No handler for %s command!${coff}" % packet._name, level="error" )

				response = Fail( packet._sequence, "UnavailablePermanently", "Command '%s' not supported!" % packet._name )
			else:
				msg( "${wht1}Calling ${mgt1}%s${wht1} handler method.${coff}" % handler.__class__.__name__ )

				try:
					response = handler( packet )
				except Exception, ex:
					err()
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

	@logctx
	def connectionLost( self, reason ):
		pass

	def logPrefix( self ):
		return self.__class__.__name__
#}}}

__all__ = [ 'ClientSessionContext', 'ClientSessionHandler' ]
