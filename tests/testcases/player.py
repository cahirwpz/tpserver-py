from templates import GetWithIDWhenNotLogged, WithIDTestMixin, GetItemWithID
from testenv import GameTestEnvMixin

class GetPlayerMixin( WithIDTestMixin ):
	__request__  = 'GetPlayer'
	__response__ = 'Player'

	__attrs__   = [ 'id' ]
	__attrmap__ = dict( name = 'username' )
	__attrfun__ = [] 


class GetCurrentPlayer( GetItemWithID, GetPlayerMixin, GameTestEnvMixin ):
	""" Does server respond with current player information? """

	@property
	def sign_in_as( self ):
		return self.players[1]

	@property
	def item( self ):
		return self.players[1]

	def getId( self, item ):
		return 0

class GetExistingPlayer( GetItemWithID, GetPlayerMixin, GameTestEnvMixin ):
	""" Does server respond properly if asked about existing player? """

	@property
	def item( self ):
		return self.players[1]

class GetNonExistentPlayer( GetItemWithID, GetPlayerMixin, GameTestEnvMixin ):
	""" Does server fail to respond if asked about nonexistent player? """

	@property
	def item( self ):
		return self.players[0]
	
	def getId( self, item ):
		return self.item.id + 666

	def getFail( self, item ):
		return 'NoSuchThing'

class GetAllAvailablePlayers( GetItemWithID, GetPlayerMixin, GameTestEnvMixin ):
	""" Does server return sequence of Player packets if asked about two players? """

	@property
	def items( self ):
		return self.players

class GetPlayerWhenNotLogged( GetWithIDWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetPlayers request? """

	__request__ = 'GetPlayer'

__all__ = [	'GetCurrentPlayer', 
			'GetExistingPlayer', 
			'GetNonExistentPlayer', 
			'GetAllAvailablePlayers', 
			'GetPlayerWhenNotLogged' ]
