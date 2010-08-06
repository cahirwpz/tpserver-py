from test import TestSuite
from common import AuthorizedTestSession, Expect

from tp.server.model import DatabaseManager

class GetExistingMessage( AuthorizedTestSession ):
	""" Does server respond properly if asked about existing message? """

	def __iter__( self ):
		board   = self.ctx['board']
		message = board.messages[2]

		GetMessage = self.protocol.use( 'GetMessage' )

		packet = yield GetMessage( self.seq, board.id, [ message.id ] ), Expect( 'Message' )

		if packet.id != board.id:
			self.failed( "Server responded with different BoardId than requested!" )

		if packet.slot != message.id:
			self.failed( "Server responded with different SlotId than requested!" )

class GetNonExistentMessage1( AuthorizedTestSession ):
	""" Does server fail to respond if asked about non-existent message (wrong MessageId)? """

	NoFailAllowed = False

	def __iter__( self ):
		board   = self.ctx['board']
		message = board.messages[2]

		GetMessage = self.protocol.use( 'GetMessage' )

		packet = yield GetMessage( self.seq, board.id + 1000, [ message.id ] ), Expect( 'Message', ('Fail', 'NoSuchThing') )

		if packet.type == 'Message':
			self.failed( "Server does return information for non-existent MessageId = %d!" % self.WrongMessageId )

class GetNonExistentMessage2( AuthorizedTestSession ):
	""" Does server fail to respond if asked about non-existent message (wrong SlotId)? """

	NoFailAllowed = False

	def __iter__( self ):
		board   = self.ctx['board']
		message = board.messages[2]

		GetMessage = self.protocol.use( 'GetMessage' )

		packet = yield GetMessage( self.seq, board.id, [ message.id + 1000 ] ), Expect( 'Message', ('Fail', 'NoSuchThing') )

		if packet.type == 'Message':
			self.failed( "Server does return information for non-existent Message (MessageId = 1, SlotId = %d)!" % self.WrongSlotId )

class GetMultipleMessages( AuthorizedTestSession ):
	""" Does server return sequence of Message packets if asked about two messages? """

	def __iter__( self ):
		board   = self.ctx['board']
		message1 = board.messages[0]
		message3 = board.messages[2]

		GetMessage = self.protocol.use( 'GetMessage' )

		s, p1, p2 = yield GetMessage( self.seq, board.id, [ message3.id, message1.id ] ), Expect( ('Sequence', 2, 'Message' ) )

		if p1.id != board.id or p2.id != board.id:
			self.failed( "Server responded with different BoardId than requested!" )

		if p1.slot != message3.id or p2.slot != message1.id:
			self.failed( "Server returned different MessageSlots (%d,%d) than requested (%d,%d)." % (p1.id, p2.id, message3.id, message1.id) )

class PutMessage( AuthorizedTestSession ):
	""" Tries to send message to default board. """

	def __iter__( self ):
		Message = self.protocol.use( 'Message' )

		packet = yield Message( self.seq, 1, -1, [], "Bla", "Foobar", 0, [] ), Expect( 'Okay', ('Fail', 'NoSuchThing') )

class MessageTestSuite( TestSuite ):
	__name__  = 'Messages'
	__tests__ = [ GetExistingMessage, GetNonExistentMessage1, GetNonExistentMessage2, GetMultipleMessages ]

	def setUp( self ):
		game = self.ctx['game']

		Board, Message = game.objects.use( 'Board', 'Message' )

		board = Board(
			owner		= self.ctx['players'][0],
			name        = "First message board for %s" % self.ctx['players'][0].username,
			description = "Board for testing purposes." )

		board.messages.append(
			Message(
				subject = "First",
				body	= "Test message generated in first turn",
				turn    = 1 ))

		board.messages.append(
			Message(
				subject = "Second",
				body	= "Test message generated in second turn",
				turn    = 2 ))

		board.messages.append(
			Message(
				subject = "Third",
				body	= "Test message generated in third turn",
				turn    = 3 ))

		with DatabaseManager().session() as session:
			session.add( board )

		self.ctx['board'] = board
	
	def tearDown( self ):
		with DatabaseManager().session() as session:
			self.ctx['board'].remove( session )

__tests__ = [ MessageTestSuite ]
