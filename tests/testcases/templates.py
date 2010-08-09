from common import ConnectedTestSession, Expect 

class GetWithIDWhenNotLogged( ConnectedTestSession ):#{{{
	__request__ = None

	def __iter__( self ):
		Request = self.protocol.use( self.__request__ )

		yield Request( self.seq, [1] ), Expect( ('Fail', 'UnavailableTemporarily') )
#}}}

class WhenNotLogged( ConnectedTestSession ):#{{{
	__request__ = None

	def __iter__( self ):
		RequestType = self.protocol.use( self.__request__ )

		yield self.makeRequest( RequestType ), Expect( ('Fail', 'UnavailableTemporarily') )
#}}}

class GetWithIDSlotWhenNotLogged( WhenNotLogged ):#{{{
	def makeRequest( self, GetWithID ):
		return GetWithID( self.seq, 1, [1] )
#}}}

class GetIDSequenceWhenNotLogged( ConnectedTestSession ):#{{{
	def makeRequest( self, IDSequence):
		return IDSequence( self.seq, -1, 0, -1 )
#}}}

__all__ = [ 'GetWithIDWhenNotLogged', 'GetIDSequenceWhenNotLogged',
			'GetWithIDSlotWhenNotLogged', 'WhenNotLogged' ]
