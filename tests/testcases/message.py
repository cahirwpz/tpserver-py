from common import ExpectSequence
from templates import AuthorizedTestSession, WhenNotLogged, GetWithIDSlotWhenNotLogged, WithIDTestMixin
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

class GetMessageMixin( WithIDTestMixin ):
	__request__  = 'GetMessage'
	__response__ = 'Message'

	__attrs__   = [ 'subject' ]
	__attrmap__ = {}
	__attrfun__ = [ 'id', 'slot' ]

	def convert_id( self, packet, obj ):
		return packet.id, obj.board.id

	def convert_slot( self, packet, obj ):
		return packet.slot, obj.id

class GetExistingMessage( AuthorizedTestSession, GetMessageMixin, MessageTestEnvMixin ):
	""" Does server respond properly if asked about existing message? """

	@property
	def item( self ):
		return self.board.messages[2]

	def __iter__( self ):
		GetMessage = self.protocol.use( 'GetMessage' )

		packet = yield GetMessage( self.seq, self.item.board.id, [ self.item.id ] )

		self.assertPacket( packet, 'Message' )
		self.assertPacketEqual( packet, self.item )

class GetNonExistentMessage1( AuthorizedTestSession, MessageTestEnvMixin ):
	""" Does server fail to respond if asked about non-existent message (wrong MessageId)? """

	@property
	def item( self ):
		return self.board.messages[2]

	def __iter__( self ):
		GetMessage = self.protocol.use( 'GetMessage' )

		packet = yield GetMessage( self.seq, self.item.board.id + 666, [ self.item.id ] )

		self.assertPacketFail( packet, 'NoSuchThing',
				"Server does return information for non-existent BoardId = %d!" % ( self.item.board.id + 666 ) )

class GetNonExistentMessage2( AuthorizedTestSession, MessageTestEnvMixin ):
	""" Does server fail to respond if asked about non-existent message (wrong SlotId)? """

	@property
	def item( self ):
		return self.board.messages[2]

	def __iter__( self ):
		GetMessage = self.protocol.use( 'GetMessage' )

		packet = yield GetMessage( self.seq, self.item.board.id, [ self.item.id + 666 ] )

		self.assertPacketFail( packet, 'NoSuchThing',
				"Server does return information for non-existent Message (BoardId = %d, SlotId = %d)!" % ( self.item.board.id, self.item.id + 666 ) )

class GetMultipleMessages( AuthorizedTestSession, GetMessageMixin, MessageTestEnvMixin ):
	""" Does server return sequence of Message packets if asked about two messages? """

	@property
	def items( self ):
		return [ self.board.messages[0], self.board.messages[2] ]

	def __iter__( self ):
		GetMessage = self.protocol.use( 'GetMessage' )

		response = yield GetMessage( self.seq, self.board.id, [ item.id for item in self.items ] )

		self.assertPacketType( response, ExpectSequence( 2, 'Message' ) )
		self.assertPacketSeqEqual( response, self.items )

class PostMessage( AuthorizedTestSession, MessageTestEnvMixin ):
	""" Tries to send message to default board. """

	def setUp( self ):
		self.msg_subject = "Blah"

	def __iter__( self ):
		PostMessage = self.protocol.use('PostMessage')
		Message = self.model.use('Message')

		response = yield PostMessage( self.seq, 1, -1, [], self.msg_subject, "Foobar", 0, [] )

		self.assertPacket( response, 'Okay' )

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

__all__ = [	'GetExistingMessage', 
			'GetNonExistentMessage1', 
			'GetNonExistentMessage2', 
			'GetMultipleMessages', 
			'PostMessage', 
			'GetMessageWhenNotLogged', 
			'RemoveMessageWhenNotLogged', 
			'PostMessageWhenNotLogged' ]
