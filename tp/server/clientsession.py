from logging import logctx, msg, err

from tp.server.bases import Player

from cmdhandler import CommandsHandler
from packet import PacketFactory

class ClientData( object ):#{{{
	def __init__( self ):
		self.game     = None
		self.ruleset  = None
		self.__player = None

	@property
	def player( self ):
		return self.__player

	@player.setter
	def player( self, value ):
		if value is None:
			self.__player = None
			#self.game    = None		
			#self.ruleset = None

		elif isinstance( value, Player ):
			self.__player = value
			#self.game    = value.playing
			#self.ruleset = value.playing.ruleset
		else:
			raise TypeError( "Player value must either be None or a Player object!" )
#}}}

class ClientSessionHandler( object ):#{{{
	def __init__( self ):
		self._objects = PacketFactory().objects
		self._client = ClientData()
		self._commands = dict( CommandsHandler( self._objects, self._client ).commands() )
		
		self.lastSeq = None

	@logctx
	def sessionStarted( self, protocol ):
		self.protocol = protocol

	@logctx
	def packetReceived( self, packet ):
		msg( "${wht1}Going to deal with ${mgt1}%s${wht1} packet.${coff}" % packet._name )

		if self.lastSeq != None:
			if self.lastSeq >= packet._sequence:
				self.sendResponse( self._objects.Fail( packet._sequence, "Frame", "Wrong sequence number!", [] ) )
				return
			else:
				self.lastSeq = packet._sequence
		else:
			self.lastSeq = packet._sequence

		try:
			handler = self._commands[ packet._name ]
		except KeyError:
			msg( "${red1}No handler for %s command!${coff}" % packet._name, level="error" )

			response = self._objects.Fail( packet._sequence, "UnavailablePermanently", "Command '%s' not supported!" % packet._name )
		else:
			msg( "${wht1}Calling ${mgt1}%s${wht1} handler method.${coff}" % handler.__name__ )

			try:
				response = handler( packet )
			except Exception, ex:
				err()
				response = None
			
			if not response:
				response = self._objects.Fail( packet._sequence, "UnavailablePermanently", "Internal server error!", [])

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
