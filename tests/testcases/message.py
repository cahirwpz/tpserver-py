from common import AuthorizedTestSession, Expect

class GetExistingMessage( AuthorizedTestSession ):
	""" Does server respond properly if asked about existing message? """

	def __iter__( self ):
		packet = yield self.protocol.GetMessage( self.seq, 1, [0] ), Expect( 'Message' )

		if packet.id != 1:
			self.failed( "Server responded with different MessageId than requested!" )

class GetNonExistentMessage1( AuthorizedTestSession ):
	""" Does server fail to respond if asked about non-existent message (wrong MessageId)? """

	NoFailAllowed = False
	WrongMessageId = 666

	def __iter__( self ):
		packet = yield self.protocol.GetMessage( self.seq, self.WrongMessageId, [0] ), Expect( 'Message', ('Fail', 'NoSuchThing') )

		if packet.type == 'Message':
			self.failed( "Server does return information for non-existent MessageId = %d!" % self.WrongMessageId )

class GetNonExistentMessage2( AuthorizedTestSession ):
	""" Does server fail to respond if asked about non-existent message (wrong SlotId)? """

	NoFailAllowed = False
	WrongSlotId = 666

	def __iter__( self ):
		packet = yield self.protocol.GetMessage( self.seq, 1, [self.WrongSlotId] ), Expect( 'Message', ('Fail', 'NoSuchThing') )

		if packet.type == 'Message':
			self.failed( "Server does return information for non-existent Message (MessageId = 1, SlotId = %d)!" % self.WrongSlotId )

class GetMultipleMessages( AuthorizedTestSession ):
	""" Does server return sequence of Message packets if asked about two messages? """

	def __iter__( self ):
		s, p1, p2 = yield self.protocol.GetMessage( self.seq, 1, [0,1] ), Expect( ('Sequence', 2, 'Message' ) )

		if p1.id != 1 or p2.id != 2:
			self.failed( "Server returned different MessageIds (%d,%d) than requested (1,2)." % (p1.id, p2.id) )

__tests__ = [ GetExistingMessage, GetNonExistentMessage1, GetNonExistentMessage2 ]
