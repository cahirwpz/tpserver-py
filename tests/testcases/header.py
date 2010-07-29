from common import TestSession, Expect

class SameSequenceInHeader( TestSession ):
	""" Checks if a server drops second packet with same sequence. """

	NoFailAllowed = False

	def __iter__( self ):
		Connect, Ping = self.protocol.use( 'Connect', 'Ping' )

		yield Connect( 1, "tpserver-tests client" ), Expect( 'Okay' )
		yield Ping( 2 ), Expect( 'Okay' )

		packet = yield Ping( 2 ), Expect( 'Fail' )

		if packet._name == 'Okay':
			self.status = False
			self.reason = "Server does accept multiple packets with same sequence number!"
		else:
			self.status = True

__tests__ = [ SameSequenceInHeader ]
