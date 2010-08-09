from test import TestSuite
from common import AuthorizedTestSession, Expect
from templates import GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged, WhenNotLogged

from tp.server.model import DatabaseManager

class GetExistingCategory( AuthorizedTestSession ):#{{{
	""" Does server respond properly if asked about existing category? """

	def __iter__( self ):
		category = self.ctx['categories'][3]

		GetCategory = self.protocol.use( 'GetCategory' )

		packet = yield GetCategory( self.seq, [ category.id ] ), Expect( 'Category' )

		assert packet.id == category.id, \
			"Server responded with different CategoryId than requested!"
#}}}

class GetNonExistentCategory( AuthorizedTestSession ):#{{{
	""" Does server fail to respond if asked about nonexistent category? """

	def __iter__( self ):
		category = self.ctx['categories'][3]

		GetCategory = self.protocol.use( 'GetCategory' )

		packet = yield GetCategory( self.seq, [ category.id + 666 ] ), Expect( 'Category', ('Fail', 'NoSuchThing') )

		assert packet.type != 'Category', \
			"Server does return information for non-existent CategoryId = %s!" % ( category.id + 666 )
#}}}

class GetMultipleCategories( AuthorizedTestSession ):#{{{
	""" Does server return sequence of Category packets if asked about two categories? """

	def __iter__( self ):
		categories = self.ctx['categories']

		c1 = categories[3]
		c2 = categories[0]
		c3 = categories[1]

		GetCategory = self.protocol.use( 'GetCategory' )

		s, p1, p2, p3 = yield GetCategory( self.seq, [ c1.id, c2.id, c3.id ] ), Expect( ('Sequence', 3, 'Category' ) )

		assert p1.id == c1.id and p2.id == c2.id and p3.id == c3.id, \
			"Server returned different CategoryIds (%d,%d,%d) than requested (%d,%d,%d)." % (p1.id, p2.id, p3.id, c1.id, c2.id, c3.id)
#}}}

class GetAllCategoryIDs( AuthorizedTestSession ):#{{{
	""" Does server return proper sequence of Category id numbers? """

	def __iter__( self ):
		GetCategoryIDs = self.protocol.use( 'GetCategoryIDs' )

		packet = yield GetCategoryIDs( self.seq, -1, 0, -1 ), Expect( 'CategoryIDs' )

		assert packet.remaining == 4
#}}}

class GetCategoryWhenNotLogged( GetWithIDWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetCategory request? """

	__request__ = 'GetCategory'
#}}}

class GetCategoryIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetCategoryIDs request? """

	__request__ = 'GetCategoryIDs'
#}}}

class AddCategoryWhenNotLogged( WhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got AddCategory request? """

	__request__ = 'AddCategory'

	def makeRequest( self, AddCategory ):
		return AddCategory( self.seq, -1, 0, "Category", "Category used for testing purposes" )
#}}}

class RemoveCategoryWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got RemoveCategory request? """

	__request__ = 'RemoveCategory'
#}}}

class CategoryTestSuite( TestSuite ):#{{{
	__name__  = 'Categories'
	__tests__ = [ GetCategoryWhenNotLogged, GetCategoryIDsWhenNotLogged,
			AddCategoryWhenNotLogged, RemoveCategoryWhenNotLogged,
			GetExistingCategory, GetNonExistentCategory, GetMultipleCategories,
			GetAllCategoryIDs ]

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
#}}}

__tests__ = [ CategoryTestSuite ]
