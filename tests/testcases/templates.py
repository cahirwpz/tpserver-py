from common import AuthorizedTestSession, ConnectedTestSession, Expect 

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

class GetItemWithID( AuthorizedTestSession ):#{{{
	"""
	Must provide two class attributes:
	__request__  name of a request
	__response__ name of a expected response
	"""

	@property
	def item( self ):
		raise NotImplementedError

	@property
	def itemId( self ):
		return self.item.id

	def __iter__( self ):
		Request = self.protocol.use( self.__request__ )

		if hasattr( self, '__fail__' ):
			expect = Expect( self.__response__, ( 'Fail', self.__fail__ ) )
		else:
			expect = Expect( self.__response__ )

		packet = yield Request( self.seq, [ self.itemId ] ), expect

		if hasattr( self, '__fail__' ):
			if self.__fail__ == 'NoSuchThing':
				code = 4
				msg  = "Server does return information for non-existent %s.Id (%s)!" % ( self.__response__, self.itemId )
			elif self.__fail__ == 'PermissionDenied':
				code = 5
				msg  = "Server does allow to access a %s.Id (%s) while it should be disallowed!" % ( self.__response__, self.itemId )
			else:
				raise NotImplementedError

			assert packet.type == 'Fail' and packet.code == code, msg
		else:
			self.assertEqual( packet, self.item )
#}}}

__all__ = [ 'GetWithIDWhenNotLogged', 'GetIDSequenceWhenNotLogged',
			'GetWithIDSlotWhenNotLogged', 'WhenNotLogged', 'GetItemWithID' ]
