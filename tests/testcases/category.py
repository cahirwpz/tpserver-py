from test import TestSuite
from common import AuthorizedTestSession, Expect, ExpectSequence, ExpectFail, ExpectOneOf, TestSessionUtils
from templates import GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged, WhenNotLogged, GetItemWithID

from tp.server.model import Model

class GetCategoryMixin( TestSessionUtils ):#{{{
	__request__  = 'GetCategory'
	__response__ = 'Category'

	def assertEqual( self, packet, category ):
		for attr in [ 'id', 'name', 'description', 'modtime' ]:
			pval = getattr( packet, attr, None )

			if attr == 'modtime':
				bval = self.datetimeToInt( category.mtime )
			else:
				bval = getattr( category, attr, None )

			assert pval == bval, \
					"Server responded with different %s.%s (%s) than expected (%s)!" % ( self.__response__, attr.title(), pval, bval )
#}}}

class GetExistingCategory( GetItemWithID, GetCategoryMixin ):#{{{
	""" Does server respond properly if asked about existing category? """

	@property
	def item( self ):
		return self.ctx['categories'][0]
#}}}

class GetNonExistentCategory( GetItemWithID, GetCategoryMixin ):#{{{
	""" Does server fail to respond if asked about nonexistent category? """

	__fail__ = 'NoSuchThing'

	@property
	def item( self ):
		return self.ctx['categories'][0]
	
	def getId( self, item ):
		return self.item.id + 666
#}}}

class GetPublicCategory( GetItemWithID, GetCategoryMixin ):#{{{
	""" Does server allow to fetch public Category? """

	@property
	def item( self ):
		return self.ctx['categories'][3]
#}}}

class GetPrivateCategory( GetItemWithID, GetCategoryMixin ):#{{{
	""" Does server allow to fetch private Category owned by the player? """

	@property
	def item( self ):
		return self.ctx['categories'][1]
#}}}

class GetOtherPlayerPrivateCategory( GetItemWithID, GetCategoryMixin ):#{{{
	""" Does server disallow to fetch private Category of another player? """

	__fail__ = 'PermissionDenied'

	@property
	def item( self ):
		return self.ctx['categories'][2]
#}}}

class GetMultipleCategories( AuthorizedTestSession ):#{{{
	""" Does server return sequence of Category packets if asked about two categories? """

	def __iter__( self ):
		categories = self.ctx['categories']

		c1 = categories[3]
		c2 = categories[0]
		c3 = categories[1]

		GetCategory = self.protocol.use( 'GetCategory' )

		s, p1, p2, p3 = yield GetCategory( self.seq, [ c1.id, c2.id, c3.id ] ), ExpectSequence(3, 'Category')

		assert p1.id == c1.id and p2.id == c2.id and p3.id == c3.id, \
			"Server returned different CategoryIds (%d,%d,%d) than requested (%d,%d,%d)." % (p1.id, p2.id, p3.id, c1.id, c2.id, c3.id)
#}}}

class GetAllCategoryIDs( AuthorizedTestSession ):#{{{
	""" Does server return proper sequence of Category id numbers? """

	def __iter__( self ):
		GetCategoryIDs = self.protocol.use( 'GetCategoryIDs' )

		packet = yield GetCategoryIDs( self.seq, -1, 0, -1 ), Expect( 'CategoryIDs' )

		assert packet.remaining == 3, "Expected to get three Categories."
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

class AddNewCategory( AuthorizedTestSession, GetCategoryMixin ):#{{{
	""" Is server able to add new category? """

	def __iter__( self ):
		AddCategory = self.protocol.use( 'AddCategory' )
		Category = self.game.objects.use( 'Category' )

		packet = yield AddCategory( self.seq, -1, 0, "Test", "Category for testing purposes." ), Expect( 'Category' )

		self.cat = Category.ById( packet.id )

		self.assertEqual( packet, self.cat )

	def tearDown( self ):
		if hasattr( self, 'cat' ):
			Model.remove( self.cat )
#}}}

class AddCategoryButSameExists( AuthorizedTestSession, GetCategoryMixin ):#{{{
	""" Does server properly reject creating already existing private category? """

	def setUp( self ):
		self.cat_name = "Test"

		Category = self.game.objects.use( 'Category' )

		self.cat = Category(
				name = self.cat_name,
				owner = self.ctx['players'][0],
				description = "Private Category for testing purposes." )

		Model.add( self.cat )

	def __iter__( self ):
		AddCategory = self.protocol.use( 'AddCategory' )
		Category = self.game.objects.use( 'Category' )

		packet = yield AddCategory( self.seq, -1, 0, self.cat_name, "Category for testing purposes." ), \
				ExpectOneOf( 'Category', ExpectFail('PermissionDenied') )

		if packet.type == 'Category':
			self.wrong_cat = Category.ById( packet.id )

		assert packet.type == 'Fail', \
				"%s must not be added if %s exists!" % ( self.wrong_cat, self.cat )

	def tearDown( self ):
		Model.remove( getattr( self, 'cat', None ), getattr( self, 'wrong_cat', None ) )
#}}}

class AddCategoryWithSameNameAsPrivate( AuthorizedTestSession, GetCategoryMixin ):#{{{
	""" Does server allow to add new category with same name but different player ? """

	def setUp( self ):
		self.cat_name = "Test"

		Category = self.game.objects.use( 'Category' )

		self.other_cat = Category(
				name = self.cat_name,
				owner = self.ctx['players'][1],
				description = "Private Category for testing purposes." )

		Model.add( self.other_cat )

	def __iter__( self ):
		AddCategory = self.protocol.use( 'AddCategory' )
		Category = self.game.objects.use( 'Category' )

		packet = yield AddCategory( self.seq, -1, 0, self.cat_name, "Category for testing purposes." ), \
				Expect('Category')

		self.cat = Category.ById( packet.id )

		self.assertEqual( packet, self.cat )

	def tearDown( self ):
		Model.remove( getattr( self, 'cat', None ), getattr( self, 'other_cat', None ) )
#}}}

class AddCategoryWithSameNameAsPublic( AuthorizedTestSession, GetCategoryMixin ):#{{{
	""" Does server properly reject creating already existing private category with same name as a public one? """

	def setUp( self ):
		self.cat_name = "Test"

		Category = self.game.objects.use( 'Category' )

		self.cat = Category(
				name = self.cat_name,
				description = "Public category for testing purposes." )

		Model.add( self.cat )

	def __iter__( self ):
		AddCategory = self.protocol.use( 'AddCategory' )
		Category = self.game.objects.use( 'Category' )

		packet = yield AddCategory( self.seq, -1, 0, self.cat_name, "Category for testing purposes." ), \
				ExpectOneOf( 'Category', ExpectFail('PermissionDenied') )

		if packet.type == 'Category':
			self.wrong_cat = Category.ById( packet.id )

		assert packet.type == 'Fail', \
				"%s must not be added if %s exists!" % ( self.wrong_cat, self.cat )

	def tearDown( self ):
		Model.remove( getattr( self, 'cat', None ), getattr( self, 'wrong_cat', None ) )
#}}}

class RemoveCategoryWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got RemoveCategory request? """

	__request__ = 'RemoveCategory'
#}}}

class AddCategoryTestSuite( TestSuite ):#{{{
	__name__  = 'AddCategory'
	__tests__ = [ AddCategoryWhenNotLogged, AddNewCategory,
			AddCategoryButSameExists, AddCategoryWithSameNameAsPrivate,
			AddCategoryWithSameNameAsPublic ]
#}}}

class GetCategoryTestSuite( TestSuite ):#{{{
	__name__  = 'GetCategory'
	__tests__ = [ GetCategoryWhenNotLogged, GetExistingCategory,
			GetNonExistentCategory, GetPublicCategory, GetPrivateCategory,
			GetOtherPlayerPrivateCategory, GetMultipleCategories ]
#}}}

class GetCategoryIDsTestSuite( TestSuite ):#{{{
	__name__  = 'GetCategoryIDs'
	__tests__ = [ GetCategoryIDsWhenNotLogged, GetAllCategoryIDs ]
#}}}

class RemoveCategoryTestSuite( TestSuite ):#{{{
	__name__  = 'RemoveCategory'
	__tests__ = [ RemoveCategoryWhenNotLogged ]
#}}}

class CategoryTestSuite( TestSuite ):#{{{
	__name__  = 'Categories'
	__tests__ = [ GetCategoryTestSuite, GetCategoryIDsTestSuite, AddCategoryTestSuite, RemoveCategoryTestSuite ]

	def setUp( self ):
		game = self.ctx['game']

		Category = game.objects.use( 'Category' )

		category1 = Category(
				name = "Misc",
				description = "Things which dont fit into any other category." )

		category2 = Category(
				name = "Production",
				owner = self.ctx['players'][0],
				description = "Things which deal with the production of stuff." )

		category3 = Category(
				name = "Combat",
				owner = self.ctx['players'][1],
				description = "Things which deal with combat between ships." )

		category4 = Category(
				name = "Designs",
				description = "A category which has all the designs." )

		self.ctx['categories'] = [ category1, category2, category3, category4 ]

		Model.add( *self.ctx['categories'] )
	
	def tearDown( self ):
		Model.remove( *self.ctx['categories'] )
#}}}

__tests__ = [ CategoryTestSuite ]
