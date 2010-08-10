from common import AuthorizedTestSession, ConnectedTestSession, Expect, ExpectFail, ExpectSequence, ExpectOneOf

class GetWithIDWhenNotLogged( ConnectedTestSession ):#{{{
	__request__ = None

	def __iter__( self ):
		Request = self.protocol.use( self.__request__ )

		yield Request( self.seq, [1] ), ExpectFail('UnavailableTemporarily')
#}}}

class WhenNotLogged( ConnectedTestSession ):#{{{
	__request__ = None

	def __iter__( self ):
		RequestType = self.protocol.use( self.__request__ )

		yield self.makeRequest( RequestType ), ExpectFail('UnavailableTemporarily')
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

	def getId( self, item ):
		return item.id

	def __iter__( self ):
		Request = self.protocol.use( self.__request__ )

		if hasattr( self, '__fail__' ):
			expect = ExpectOneOf( self.__response__, ExpectFail( self.__fail__ ) )
		else:
			expect = Expect( self.__response__ )

		itemId = self.getId( self.item ) 

		packet = yield Request( self.seq, [ itemId ] ), expect

		if hasattr( self, '__fail__' ):
			if self.__fail__ == 'NoSuchThing':
				code = 4
				msg  = "Server does return information for non-existent %s.Id (%s)!" % ( self.__response__, itemId )
			elif self.__fail__ == 'PermissionDenied':
				code = 5
				msg  = "Server does allow to access a %s.Id (%s) while it should be disallowed!" % ( self.__response__, itemId )
			else:
				raise NotImplementedError

			assert packet.type == 'Fail' and packet.code == code, msg
		else:
			self.assertEqual( packet, self.item )
#}}}

class GetItemsWithID( AuthorizedTestSession ):#{{{
	@property
	def items( self ):
		raise NotImplementedError

	def getId( self, item ):
		return item.id

	def __iter__( self ):
		Request = self.protocol.use( self.__request__ )

		packets = yield Request( self.seq, [ self.getId( item ) for item in self.items ] ), ExpectSequence( len( self.items ), self.__response__ )

		for p, b in zip( packets[1:], self.items ):
			self.assertEqual( p, b )
#}}}

__all__ = [ 'GetWithIDWhenNotLogged', 'GetIDSequenceWhenNotLogged',
			'GetWithIDSlotWhenNotLogged', 'WhenNotLogged', 'GetItemWithID'
			'GetItemsWithID' ]
