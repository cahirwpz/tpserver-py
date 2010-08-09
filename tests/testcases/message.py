from test import TestSuite
from common import AuthorizedTestSession, Expect
from templates import WhenNotLogged, GetWithIDSlotWhenNotLogged

from tp.server.model import DatabaseManager

class GetExistingMessage( AuthorizedTestSession ):#{{{
	""" Does server respond properly if asked about existing message? """

	def __iter__( self ):
		board   = self.ctx['board']
		message = board.messages[2]

		GetMessage = self.protocol.use( 'GetMessage' )

		packet = yield GetMessage( self.seq, board.id, [ message.id ] ), Expect( 'Message' )

		assert packet.id == board.id, \
				"Server responded with different BoardId than requested!"

		assert packet.slot == message.id, \
				"Server responded with different SlotId than requested!"
#}}}

class GetNonExistentMessage1( AuthorizedTestSession ):#{{{
	""" Does server fail to respond if asked about non-existent message (wrong MessageId)? """

	def __iter__( self ):
		board   = self.ctx['board']
		message = board.messages[2]

		GetMessage = self.protocol.use( 'GetMessage' )

		packet = yield GetMessage( self.seq, board.id + 666, [ message.id ] ), Expect( 'Message', ('Fail', 'NoSuchThing') )

		assert packet.type != 'Message', \
			"Server does return information for non-existent BoardId = %d!" % ( board.id + 666 )
#}}}

class GetNonExistentMessage2( AuthorizedTestSession ):#{{{
	""" Does server fail to respond if asked about non-existent message (wrong SlotId)? """

	def __iter__( self ):
		board   = self.ctx['board']
		message = board.messages[2]

		GetMessage = self.protocol.use( 'GetMessage' )

		packet = yield GetMessage( self.seq, board.id, [ message.id + 666 ] ), Expect( 'Message', ('Fail', 'NoSuchThing') )

		assert packet.type != 'Message', \
			"Server does return information for non-existent Message (BoardId = %d, SlotId = %d)!" % ( board.id, message.id + 666 )
#}}}

class GetMultipleMessages( AuthorizedTestSession ):#{{{
	""" Does server return sequence of Message packets if asked about two messages? """

	def __iter__( self ):
		board   = self.ctx['board']
		message1 = board.messages[0]
		message3 = board.messages[2]

		GetMessage = self.protocol.use( 'GetMessage' )

		s, p1, p2 = yield GetMessage( self.seq, board.id, [ message3.id, message1.id ] ), Expect( ('Sequence', 2, 'Message' ) )

		assert p1.id == board.id and p2.id == board.id, \
			"Server responded with different BoardId than requested!"

		assert p1.slot == message3.id and p2.slot == message1.id, \
			"Server returned different MessageSlots (%d,%d) than requested (%d,%d)." % (p1.id, p2.id, message3.id, message1.id)
#}}}

class PostMessage( AuthorizedTestSession ):#{{{
	""" Tries to send message to default board. """

	def __iter__( self ):
		PostMessage = self.protocol.use( 'PostMessage' )

		packet = yield PostMessage( self.seq, 1, -1, [], "Bla", "Foobar", 0, [] ), Expect( 'Okay', ('Fail', 'NoSuchThing') )
#}}}

class GetMessageWhenNotLogged( GetWithIDSlotWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetMessage request? """

	__request__ = 'GetMessage'
#}}}

class RemoveMessageWhenNotLogged( GetWithIDSlotWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got RemoveMessage request? """

	__request__ = 'RemoveMessage'
#}}}

class PostMessageWhenNotLogged( WhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got PostMessage request? """

	__request__ = 'PostMessage'

	def makeRequest( self, PostMessage ):
		return PostMessage( self.seq, 1, 1, [], "Subject", "Body", 0, [] )
#}}}

class MessageTestSuite( TestSuite ):#{{{
	__name__  = 'Messages'
	__tests__ = [ GetMessageWhenNotLogged, PostMessageWhenNotLogged,
			RemoveMessageWhenNotLogged, GetExistingMessage,
			GetNonExistentMessage1, GetNonExistentMessage2,
			GetMultipleMessages, PostMessage ]

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
#}}}

__tests__ = [ MessageTestSuite ]
