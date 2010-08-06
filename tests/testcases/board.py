from test import TestSuite
from common import AuthorizedTestSession, Expect

from tp.server.model import DatabaseManager

class GetCurrentBoard( AuthorizedTestSession ):
	""" Does server respond with current board information? """

	def setUp( self ):
		self.login = self.ctx['players'][1].username
		self.password = self.ctx['players'][1].password

	def __iter__( self ):
		board = self.ctx['boards'][2]

		GetBoards = self.protocol.use( 'GetBoards' )

		packet = yield GetBoards( self.seq, [0] ), Expect( 'Board' )

		if packet.id != board.id:
			self.failed( "Server responded with different BoardId than requested!" )

class GetExistingBoard( AuthorizedTestSession ):
	""" Does server respond properly if asked about existing board? """

	def __iter__( self ):
		board = self.ctx['boards'][0]

		GetBoards = self.protocol.use( 'GetBoards' )

		packet = yield GetBoards( self.seq, [ board.id ] ), Expect( 'Board' )

		if packet.id != board.id:
			self.failed( "Server responded with different BoardId than requested!" )

class GetNonExistentBoard( AuthorizedTestSession ):
	""" Does server fail to respond if asked about nonexistent board? """

	NoFailAllowed = False

	def __iter__( self ):
		board = self.ctx['boards'][0]

		GetBoards = self.protocol.use( 'GetBoards' )

		packet = yield GetBoards( self.seq, [ board.id + 666 ] ), Expect( 'Board', ('Fail', 'NoSuchThing') )

		if packet.type == 'Board':
			self.failed( "Server does return information for non-existent BoardId = %s!" % self.WrongBoardId )

class GetMultipleBoards( AuthorizedTestSession ):
	""" Does server return sequence of Board packets if asked about two boards? """

	def __iter__( self ):
		b1 = self.ctx['boards'][1]
		b2 = self.ctx['boards'][0]

		GetBoards = self.protocol.use( 'GetBoards' )

		s, p1, p2 = yield GetBoards( self.seq, [ b1.id, b2.id ] ), Expect( ('Sequence', 2, 'Board' ) )

		if p1.id != b1.id or p2.id != b2.id:
			self.failed( "Server returned different BoardIds (%d,%d) than requested (%d,%d)." % (p1.id, p2.id, b1.id, b2.id) )

class BoardTestSuite( TestSuite ):
	__name__  = 'Boards'
	__tests__ = [ GetExistingBoard, GetNonExistentBoard, GetCurrentBoard, GetMultipleBoards ]

	def setUp( self ):
		game = self.ctx['game']

		Board = game.objects.use( 'Board' )

		board1 = Board(
			owner       = self.ctx['players'][0],
			name        = "First message board for %s" % self.ctx['players'][0].username,
			description = "Board for testing purposes." )

		board2 = Board(
			owner       = self.ctx['players'][0],
			name        = "Second message board for %s" % self.ctx['players'][0].username,
			description = "Board for testing purposes." )

		board3 = Board(
			owner       = self.ctx['players'][1],
			name        = "Message board for %s" % self.ctx['players'][1].username,
			description = "Board for testing purposes." )

		self.ctx['boards'] = [ board1, board2, board3 ]

		with DatabaseManager().session() as session:
			for board in self.ctx['boards']:
				session.add( board )
	
	def tearDown( self ):
		with DatabaseManager().session() as session:
			for board in self.ctx['boards']:
				board.remove( session )

__tests__ = [ BoardTestSuite ]
