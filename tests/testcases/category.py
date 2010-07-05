from common import AuthorizedTestSession, Expect

class GetExistingCategory( AuthorizedTestSession ):
	""" Does server respond properly if asked about existing category? """

	def __iter__( self ):
		packet = yield self.protocol.GetCategory( self.seq, [1] ), Expect( 'Category' )

		if packet.id != 1:
			self.failed( "Server responded with different CategoryId than requested!" )

class GetNonExistentCategory( AuthorizedTestSession ):
	""" Does server fail to respond if asked about nonexistent category? """

	NoFailAllowed = False
	WrongCategoryId = 666

	def __iter__( self ):
		packet = yield self.protocol.GetCategory( self.seq, [self.WrongCategoryId] ), Expect( 'Category', ('Fail', 'NoSuchThing') )

		if packet.type == 'Category':
			self.failed( "Server does return information for non-existent CategoryId = %s!" % self.WrongCategoryId )

class GetMultipleCategories( AuthorizedTestSession ):
	""" Does server return sequence of Category packets if asked about two categories? """

	def __iter__( self ):
		s, p1, p2 = yield self.protocol.GetCategory( self.seq, [1, 2] ), Expect( ('Sequence', 2, 'Category' ) )

		if p1.id != 1 or p2.id != 2:
			self.failed( "Server returned different CategoryIds (%d,%d) than requested (1,2)." % (p1.id, p2.id) )

class GetAllCategoryIDs( AuthorizedTestSession ):
	""" Does server return proper sequence of Category id numbers? """

	def __iter__( self ):
		packet = yield self.protocol.GetCategoryIDs( self.seq, -1, 0, -1 ), Expect( 'CategoryIDs' )

		if packet.remaining == 0:
			self.failed( "Server responded with different CategoryId than requested!" )

__tests__ = [ GetExistingCategory, GetNonExistentCategory, GetMultipleCategories, GetAllCategoryIDs ]
