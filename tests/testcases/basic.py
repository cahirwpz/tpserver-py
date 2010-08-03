from common import ConnectedTestSession, Expect, TestSuite

class PingRequest( ConnectedTestSession ):
	""" Check if a server answers Ping packet properly. """

	def __iter__( self ):
		Ping = self.protocol.use( 'Ping' )

		yield Ping( self.seq ), Expect( 'Okay' )

class BasicRequestsTestSuite( TestSuite ):
	__name__ = "BasicRequests"

	def __init__( self ):
		TestSuite.__init__( self )

		self.addTest( PingRequest )

__tests__ = [ BasicRequestsTestSuite ]
