from test import TestSuite
from common import AuthorizedTestSession, Expect

from tp.server.model import DatabaseManager

class GetExistingCategory( AuthorizedTestSession ):
	""" Does server respond properly if asked about existing category? """

	def __iter__( self ):
		category = self.ctx['categories'][3]

		GetCategory = self.protocol.use( 'GetCategory' )

		packet = yield GetCategory( self.seq, [ category.id ] ), Expect( 'Category' )

		if packet.id != category.id:
			self.failed( "Server responded with different CategoryId than requested!" )

class GetNonExistentCategory( AuthorizedTestSession ):
	""" Does server fail to respond if asked about nonexistent category? """

	NoFailAllowed = False

	def __iter__( self ):
		category = self.ctx['categories'][3]

		GetCategory = self.protocol.use( 'GetCategory' )

		packet = yield GetCategory( self.seq, [ category.id + 666 ] ), Expect( 'Category', ('Fail', 'NoSuchThing') )

		if packet.type == 'Category':
			self.failed( "Server does return information for non-existent CategoryId = %s!" % ( category.id + 666 ) )

class GetMultipleCategories( AuthorizedTestSession ):
	""" Does server return sequence of Category packets if asked about two categories? """

	def __iter__( self ):
		categories = self.ctx['categories']

		c1 = categories[3]
		c2 = categories[0]
		c3 = categories[1]

		GetCategory = self.protocol.use( 'GetCategory' )

		s, p1, p2, p3 = yield GetCategory( self.seq, [ c1.id, c2.id, c3.id ] ), Expect( ('Sequence', 3, 'Category' ) )

		if p1.id != c1.id or p2.id != c2.id or p3.id != c3.id:
			self.failed( "Server returned different CategoryIds (%d,%d,%d) than requested (%d,%d,%d)." % (p1.id, p2.id, p3.id, c1.id, c2.id, c3.id) )

class GetAllCategoryIDs( AuthorizedTestSession ):
	""" Does server return proper sequence of Category id numbers? """

	def __iter__( self ):
		GetCategoryIDs = self.protocol.use( 'GetCategoryIDs' )

		packet = yield GetCategoryIDs( self.seq, -1, 0, -1 ), Expect( 'CategoryIDs' )

		if packet.remaining == 0:
			self.failed( "Server responded with different CategoryId than requested!" )

class CategoryTestSuite( TestSuite ):
	__name__  = 'Categories'
	__tests__ = [ GetExistingCategory, GetNonExistentCategory, GetMultipleCategories, GetAllCategoryIDs ]

	def setUp( self ):
		game = self.ctx['game']

		Category = game.objects.use( 'Category' )

		category1 = Category(
				name = "Misc",
				description = "Things which dont fit into any other category." )

		category2 = Category(
				name = "Production",
				description = "Things which deal with the production of stuff." )

		category3 = Category(
				name = "Combat",
				description = "Things which deal with combat between ships." )

		category4 = Category(
				name = "Designs",
				description = "A category which has all the designs." )

		self.ctx['categories'] = [ category1, category2, category3, category4 ]

		with DatabaseManager().session() as session:
			for category in self.ctx['categories']:
				session.add( category )
	
	def tearDown( self ):
		with DatabaseManager().session() as session:
			for category in self.ctx['categories']:
				category.remove( session )

__tests__ = [ CategoryTestSuite ]
