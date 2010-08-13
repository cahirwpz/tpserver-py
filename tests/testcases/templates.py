import time

from common import AuthorizedTestSession, ConnectedTestSession, Expect, ExpectFail, ExpectSequence, ExpectOneOf, TestSessionUtils

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

	def getFail( self, item ):
		pass

	def __iter__( self ):
		Request = self.protocol.use( self.__request__ )

		sequence = []

		for item in self.items:
			fail = self.getFail( item )

			if fail:
				sequence.append( ExpectFail( fail ) )
			else:
				sequence.append( Expect(self.__response__) )

		packets = yield Request( self.seq, [ self.getId( item ) for item in self.items ] ), ExpectSequence( *sequence )

		for p, b in zip( packets[1:], self.items ):
			if not self.getFail( b ):
				self.assertEqual( p, b )
#}}}

class GetWithIDMixin( object ):#{{{
	def convert_modtime( self, packet, obj ):
		pval = packet.modtime
		oval = long( time.mktime( time.strptime( obj.mtime.ctime() ) ) )

		return pval, oval

	def assertEqual( self, packet, obj ):
		attrs = self.__attrs__ + list( self.__attrmap__ ) + self.__attrfun__

		for attr in attrs:
			if attr in self.__attrfun__:
				pval, oval = getattr( self, 'convert_%s' % attr )( packet, obj )
			else:
				objattr = self.__attrmap__.get( attr, attr )

				pval = getattr( packet, attr )
				oval = getattr( obj, objattr )

			assert pval == oval, \
					"Server responded with different %s(%d).%s (%s) than expected (%s)!" % ( self.__response__, packet.id, attr, pval, oval )
#}}}

class GetItemIDs( AuthorizedTestSession, TestSessionUtils ):#{{{
	def __iter__( self ):
		Request = self.protocol.use( self.__request__ )

		idseq = yield Request( self.seq, -1, 0, len( self.items ) ), Expect( self.__response__ )

		assert len( idseq.modtimes ) == len( self.items ), \
				"Expected to get %d %s packets, got %d instead." % ( len( self.items ), self.__object__, len( idseq.modtimes ) )
		assert idseq.remaining == 0, \
				"Expected to get all %s objects, but %d left to be fetched." % ( self.__object__, idseq.remaining )

		cmpId = lambda a, b: cmp( a.id, b.id )

		objs = sorted( self.items, cmpId )

		for item, obj in zip( sorted( idseq.modtimes, cmpId ), objs ):
			assert item.id == obj.id, \
					"Expected id (%s) and %s.id (%s) to be equal" % ( item.id, obj.__origname__, obj.id )
			assert item.modtime == self.datetimeToInt( obj.mtime ), \
					"Expected modtime (%s) and %s.mtime (%s) to be equal." % ( item.modtime, obj.__origname__, self.datetimeToInt( obj.mtime ) )
#}}}

__all__ = [ 'GetWithIDWhenNotLogged', 'GetIDSequenceWhenNotLogged',
			'GetWithIDSlotWhenNotLogged', 'WhenNotLogged', 'GetItemWithID'
			'GetItemsWithID', 'GetWithIDMixin', 'GetItemIDs' ]
