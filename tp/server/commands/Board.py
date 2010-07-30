#!/usr/bin/env python

from Common import FactoryMixin, GetWithIDHandler, GetIDSequenceHandler

class BoardFactoryMixin( FactoryMixin ):#{{{
	def toPacket( self, request, board ):
		Board = self.protocol.use( 'Board' )

		return Board(
				request._sequence,
				board.id, 
				board.name,
				str( board.description ).strip(),
				# TODO: number of messages on the board
				0,
				self.datetimeToInt( board.mtime ) )
#}}}

class GetBoards( GetWithIDHandler, BoardFactoryMixin ):#{{{
	"""
	Request:  GetBoards :: GetWithID
	Response: Board | Sequence + Board{2,n}
	"""
	__object__ = 'Board'

	def authorize( self, board ):
		return bool( board.owner in [ None, self.player ] )

	def fetch( self, obj, id ):
		if id == 0:
			return self.player.boards[0]

		return GetWithIDHandler.fetch( self, obj, id )
#}}}

class GetBoardIDs( GetIDSequenceHandler ):#{{{
	"""
	Request:  GetBoardIDs :: GetIDSequence
	Response: IDSequence
	"""
	__packet__ = 'BoardIDs'
	__object__ = 'Board'

	@property
	def filter( self ):
		Board = self.game.objects.use( 'Board' )

		from sqlalchemy import or_

		return or_( Board.owner == self.player, Board.owner == None )
#}}}

__all__ = [ 'GetBoards', 'GetBoardIDs' ]
