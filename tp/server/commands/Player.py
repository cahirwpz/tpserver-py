#!/usr/bin/env python

from tp.server.logging import msg
from tp.server.gamemanager import GameManager

from Common import RequestHandler, GetWithIDHandler

class PlayerFactoryMixin( object ):#{{{
	def toPacket( self, request, obj ):
		Player = self.protocol.use( 'Player' )

		return Player(
				request._sequence,
				obj.id,
				obj.username,
				"" )
#}}}

class CreateAccount( RequestHandler ):#{{{
	"""
	Request:  CreateAccount
	Response: Okay | Fail
	"""
#}}}

class GetPlayer( GetWithIDHandler, PlayerFactoryMixin ):#{{{
	"""
	Request:  GetPlayer :: GetWithID
	Response: Player | Sequence + Player{2,n}
	"""
	__packet__ = 'Player'
	__object__ = 'Player'

	def fetch( self, obj, id ):
		if id == 0:
			return self.player

		return GetWithIDHandler.fetch( self, obj, id )
#}}}

class Login( RequestHandler ):#{{{
	"""
	Request:  Login
	Response: Okay | Fail
	"""

	def __call__( self, request ):
		Okay, Fail = self.protocol.use( 'Okay', 'Fail' )

		try:
			username, game_name = request.username.split('@', 1)
		except ValueError, ex:
			msg( "${yel1}%s${coff}" % ex, level="info" )

			return Fail( request._sequence, "UnavailablePermanently", "Usernames should be of the form <username>@<game>!" )

		try:
			game = GameManager()[ game_name ]
		except KeyError, ex:
			msg( "${yel1}%s${coff}" % ex, level="info" )

			return Fail( request._sequence, "UnavailablePermanently",  "The game you specified is not valid!" )

		Player = game.objects.use( 'Player' )

		player = Player.ByName( username, request.password )

		if player is not None:
			self.context.game   = game
			self.context.player = player 

			return Okay( request._sequence, "Welcome user '%s' in game '%s'!" % ( username, game ) )
		else:
			return Fail( request._sequence, "NoSuchThing", "Login incorrect or unknown username!" )
#}}}

__all__ = [ 'CreateAccount', 'GetPlayer', 'Login' ]
