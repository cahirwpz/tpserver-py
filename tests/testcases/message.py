from test import TestSuite
from common import AuthorizedTestSession, Expect, ExpectFail, ExpectSequence, ExpectOneOf
from templates import WhenNotLogged, GetWithIDSlotWhenNotLogged, GetWithIDMixin
from testenv import GameTestEnvMixin

from tp.server.model import Model

class MessageTestEnvMixin( GameTestEnvMixin ):
	def setUp( self ):
		Board, Message = self.model.use( 'Board', 'Message' )

		board = Board(
			owner		= self.players[0],
			name        = "First message board for %s" % self.players[0].username,
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

		self.board = board

		Model.add( board )
	
	def tearDown( self ):
		Model.remove( self.board )

class GetMessageMixin( GetWithIDMixin ):
	__request__  = 'GetMessage'
	__response__ = 'Message'

	__attrs__   = [ 'id', 'slot', 'subject' ]
	__attrmap__ = {}
	__attrfun__ = [ 'modtime' ]

class GetExistingMessage( AuthorizedTestSession, MessageTestEnvMixin ):
	""" Does server respond properly if asked about existing message? """

	def __iter__( self ):
		board   = self.board
		message = board.messages[2]

		GetMessage = self.protocol.use( 'GetMessage' )

		packet = yield GetMessage( self.seq, board.id, [ message.id ] ), Expect( 'Message' )

		assert packet.id == board.id, \
				"Server responded with different BoardId than requested!"

		assert packet.slot == message.id, \
				"Server responded with different SlotId than requested!"

class GetNonExistentMessage1( AuthorizedTestSession, MessageTestEnvMixin ):
	""" Does server fail to respond if asked about non-existent message (wrong MessageId)? """

	def __iter__( self ):
		board   = self.board
		message = board.messages[2]

		GetMessage = self.protocol.use( 'GetMessage' )

		packet = yield GetMessage( self.seq, board.id + 666, [ message.id ] ), ExpectOneOf( 'Message', ExpectFail('NoSuchThing') )

		assert packet.type != 'Message', \
			"Server does return information for non-existent BoardId = %d!" % ( board.id + 666 )

class GetNonExistentMessage2( AuthorizedTestSession, MessageTestEnvMixin ):
	""" Does server fail to respond if asked about non-existent message (wrong SlotId)? """

	def __iter__( self ):
		board   = self.board
		message = board.messages[2]

		GetMessage = self.protocol.use( 'GetMessage' )

		packet = yield GetMessage( self.seq, board.id, [ message.id + 666 ] ), ExpectOneOf( 'Message', ExpectFail('NoSuchThing') )

		assert packet.type != 'Message', \
			"Server does return information for non-existent Message (BoardId = %d, SlotId = %d)!" % ( board.id, message.id + 666 )

class GetMultipleMessages( AuthorizedTestSession, MessageTestEnvMixin ):
	""" Does server return sequence of Message packets if asked about two messages? """

	def __iter__( self ):
		board   = self.board
		message1 = board.messages[0]
		message3 = board.messages[2]

		GetMessage = self.protocol.use( 'GetMessage' )

		s, p1, p2 = yield GetMessage( self.seq, board.id, [ message3.id, message1.id ] ), ExpectSequence(2, 'Message')

		assert p1.id == board.id and p2.id == board.id, \
			"Server responded with different BoardId than requested!"

		assert p1.slot == message3.id and p2.slot == message1.id, \
			"Server returned different MessageSlots (%d,%d) than requested (%d,%d)." % (p1.id, p2.id, message3.id, message1.id)

class PostMessage( AuthorizedTestSession, MessageTestEnvMixin ):
	""" Tries to send message to default board. """

	def setUp( self ):
		self.msg_subject = "Blah"

	def __iter__( self ):
		PostMessage = self.protocol.use('PostMessage')
		Message = self.model.use('Message')

		yield PostMessage( self.seq, 1, -1, [], self.msg_subject, "Foobar", 0, [] ), Expect( 'Okay' )

		messages = Message.query().filter_by( subject = self.msg_subject ).all()

		assert len( messages ) == 1, "Expected to get only one message with subject '%s'." % self.msg_subject

		self.msg = messages[0]
	
	def tearDown( self ):
		Model.remove( getattr( self, 'msg', None ) )

class GetMessageWhenNotLogged( GetWithIDSlotWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetMessage request? """

	__request__ = 'GetMessage'

class RemoveMessageWhenNotLogged( GetWithIDSlotWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got RemoveMessage request? """

	__request__ = 'RemoveMessage'

class PostMessageWhenNotLogged( WhenNotLogged ):
	""" Does a server respond properly when player is not logged but got PostMessage request? """

	__request__ = 'PostMessage'

	def makeRequest( self, PostMessage ):
		return PostMessage( self.seq, 1, 1, [], "Subject", "Body", 0, [] )

class MessageTestSuite( TestSuite ):
	__name__  = 'Messages'
	__tests__ = [ GetMessageWhenNotLogged, PostMessageWhenNotLogged,
			RemoveMessageWhenNotLogged, GetExistingMessage,
			GetNonExistentMessage1, GetNonExistentMessage2,
			GetMultipleMessages, PostMessage ]

__tests__ = [ MessageTestSuite ]
