from test import TestSuite
from common import AuthorizedTestSession, Expect, ExpectFail, ExpectOneOf
from templates import ( GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged,
		WhenNotLogged, GetItemWithID, GetWithIDMixin, GetItemsWithID,
		GetItemIDs )

from tp.server.model import Model

class GetCategoryMixin( GetWithIDMixin ):
	__request__  = 'GetCategory'
	__response__ = 'Category'

	__attrs__   = [ 'id', 'name', 'description' ]
	__attrmap__ = {}
	__attrfun__ = [ 'modtime' ]

class GetExistingCategory( GetItemWithID, GetCategoryMixin ):
	""" Does server respond properly if asked about existing category? """

	@property
	def item( self ):
		return self.ctx['categories'][0]

class GetNonExistentCategory( GetItemWithID, GetCategoryMixin ):
	""" Does server fail to respond if asked about nonexistent category? """

	__fail__ = 'NoSuchThing'

	@property
	def item( self ):
		return self.ctx['categories'][0]
	
	def getId( self, item ):
		return self.item.id + 666

class GetPublicCategory( GetItemWithID, GetCategoryMixin ):
	""" Does server allow to fetch public Category? """

	@property
	def item( self ):
		return self.ctx['categories'][3]

class GetPrivateCategory( GetItemWithID, GetCategoryMixin ):
	""" Does server allow to fetch private Category owned by the player? """

	@property
	def item( self ):
		return self.ctx['categories'][1]

class GetOtherPlayerPrivateCategory( GetItemWithID, GetCategoryMixin ):
	""" Does server disallow to fetch private Category of another player? """

	__fail__ = 'PermissionDenied'

	@property
	def item( self ):
		return self.ctx['categories'][2]

class GetMultipleCategories( GetItemsWithID, GetCategoryMixin ):
	""" Does server return sequence of Category packets if asked about two categories? """

	@property
	def items( self ):
		return [ self.ctx['categories'][3], self.ctx['categories'][0], self.ctx['categories'][1] ]

class GetAllCategoryIDs( GetItemIDs ):
	""" Does server return the IDs of all available Categories? """

	__request__  = 'GetCategoryIDs'
	__response__ = 'CategoryIDs'
	__object__   = 'Category'

	@property
	def items( self ):
		return [ self.ctx['categories'][3], self.ctx['categories'][0], self.ctx['categories'][1] ]

class GetCategoryWhenNotLogged( GetWithIDWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetCategory request? """

	__request__ = 'GetCategory'

class GetCategoryIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetCategoryIDs request? """

	__request__ = 'GetCategoryIDs'

class AddCategoryWhenNotLogged( WhenNotLogged ):
	""" Does a server respond properly when player is not logged but got AddCategory request? """

	__request__ = 'AddCategory'

	def makeRequest( self, AddCategory ):
		return AddCategory( self.seq, -1, 0, "Category", "Category used for testing purposes" )

class AddNewCategory( AuthorizedTestSession, GetCategoryMixin ):
	""" Is server able to add new category? """

	def __iter__( self ):
		AddCategory = self.protocol.use( 'AddCategory' )
		Category = self.model.use( 'Category' )

		packet = yield AddCategory( self.seq, -1, 0, "Test", "Category for testing purposes." ), Expect( 'Category' )

		self.cat = Category.ById( packet.id )

		self.mustBeEqual( packet, self.cat )

	def tearDown( self ):
		if hasattr( self, 'cat' ):
			Model.remove( self.cat )

class AddCategoryButSameExists( AuthorizedTestSession, GetCategoryMixin ):
	""" Does server properly reject creating already existing private category? """

	def setUp( self ):
		self.cat_name = "Test"

		Category = self.model.use( 'Category' )

		self.cat = Category(
				name = self.cat_name,
				owner = self.ctx['players'][0],
				description = "Private Category for testing purposes." )

		Model.add( self.cat )

	def __iter__( self ):
		AddCategory = self.protocol.use( 'AddCategory' )
		Category = self.model.use( 'Category' )

		packet = yield AddCategory( self.seq, -1, 0, self.cat_name, "Category for testing purposes." ), \
				ExpectOneOf( 'Category', ExpectFail('PermissionDenied') )

		if packet.type == 'Category':
			self.wrong_cat = Category.ById( packet.id )

		assert packet.type == 'Fail', \
				"%s must not be added if %s exists!" % ( self.wrong_cat, self.cat )

	def tearDown( self ):
		Model.remove( getattr( self, 'cat', None ), getattr( self, 'wrong_cat', None ) )

class AddCategoryWithSameNameAsPrivate( AuthorizedTestSession, GetCategoryMixin ):
	""" Does server allow to add new category with same name but different player ? """

	def setUp( self ):
		self.cat_name = "Test"

		Category = self.model.use( 'Category' )

		self.other_cat = Category(
				name = self.cat_name,
				owner = self.ctx['players'][1],
				description = "Private Category for testing purposes." )

		Model.add( self.other_cat )

	def __iter__( self ):
		AddCategory = self.protocol.use( 'AddCategory' )
		Category = self.model.use( 'Category' )

		packet = yield AddCategory( self.seq, -1, 0, self.cat_name, "Category for testing purposes." ), \
				Expect('Category')

		self.cat = Category.ById( packet.id )

		self.mustBeEqual( packet, self.cat )

	def tearDown( self ):
		Model.remove( getattr( self, 'cat', None ), getattr( self, 'other_cat', None ) )

class AddCategoryWithSameNameAsPublic( AuthorizedTestSession, GetCategoryMixin ):
	""" Does server properly reject creating already existing private category with same name as a public one? """

	def setUp( self ):
		self.cat_name = "Test"

		Category = self.model.use( 'Category' )

		self.cat = Category(
				name = self.cat_name,
				description = "Public category for testing purposes." )

		Model.add( self.cat )

	def __iter__( self ):
		AddCategory = self.protocol.use( 'AddCategory' )
		Category = self.model.use( 'Category' )

		packet = yield AddCategory( self.seq, -1, 0, self.cat_name, "Category for testing purposes." ), \
				ExpectOneOf( 'Category', ExpectFail('PermissionDenied') )

		if packet.type == 'Category':
			self.wrong_cat = Category.ById( packet.id )

		assert packet.type == 'Fail', \
				"%s must not be added if %s exists!" % ( self.wrong_cat, self.cat )

	def tearDown( self ):
		Model.remove( getattr( self, 'cat', None ), getattr( self, 'wrong_cat', None ) )

class RemoveCategoryWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got RemoveCategory request? """

	__request__ = 'RemoveCategory'

class RemovePublicCategory( AuthorizedTestSession, GetCategoryMixin ):
	""" Does server properly reject attempt to remove public category? """

	def setUp( self ):
		Category = self.model.use( 'Category' )

		self.cat = Category(
				name = "Public",
				description = "Public category for testing purposes." )

		Model.add( self.cat )

	def __iter__( self ):
		RemoveCategory = self.protocol.use( 'RemoveCategory' )

		yield RemoveCategory( self.seq, [ self.cat.id ] ), ExpectFail('PermissionDenied')

	def tearDown( self ):
		Category = self.model.use( 'Category' )

		if Category.ById( self.cat.id ):
			Model.remove( self.cat )

		super( RemovePublicCategory, self ).tearDown()

class RemovePrivateCategory( AuthorizedTestSession, GetCategoryMixin ):
	""" Does server properly reject attempt to remove public category? """

	def setUp( self ):
		Category = self.model.use( 'Category' )

		self.cat = Category(
				name = "Private1",
				owner = self.ctx['players'][0],
				description = "Private category for testing purposes." )

		Model.add( self.cat )

	def __iter__( self ):
		RemoveCategory = self.protocol.use( 'RemoveCategory' )

		yield RemoveCategory( self.seq, [ self.cat.id ] ), Expect('Okay')

	def tearDown( self ):
		Category = self.model.use( 'Category' )

		if Category.ById( self.cat.id ):
			Model.remove( self.cat )

class RemoveOtherPlayerPrivateCategory( AuthorizedTestSession, GetCategoryMixin ):
	""" Does server properly reject attempt to remove other player's private category? """

	def setUp( self ):
		Category = self.model.use( 'Category' )

		self.cat = Category(
				name = "Private2",
				owner = self.ctx['players'][1],
				description = "Private category for testing purposes." )

		Model.add( self.cat )

	def __iter__( self ):
		RemoveCategory = self.protocol.use( 'RemoveCategory' )

		yield RemoveCategory( self.seq, [ self.cat.id ] ), ExpectFail('PermissionDenied')

	def tearDown( self ):
		Category = self.model.use( 'Category' )

		if Category.ById( self.cat.id ):
			Model.remove( self.cat )

class AddCategoryTestSuite( TestSuite ):
	__name__  = 'AddCategory'
	__tests__ = [ AddCategoryWhenNotLogged, AddNewCategory,
			AddCategoryButSameExists, AddCategoryWithSameNameAsPrivate,
			AddCategoryWithSameNameAsPublic ]

class GetCategoryTestSuite( TestSuite ):
	__name__  = 'GetCategory'
	__tests__ = [ GetCategoryWhenNotLogged, GetExistingCategory,
			GetNonExistentCategory, GetPublicCategory, GetPrivateCategory,
			GetOtherPlayerPrivateCategory, GetMultipleCategories ]

class GetCategoryIDsTestSuite( TestSuite ):
	__name__  = 'GetCategoryIDs'
	__tests__ = [ GetCategoryIDsWhenNotLogged, GetAllCategoryIDs ]

class RemoveCategoryTestSuite( TestSuite ):
	__name__  = 'RemoveCategory'
	__tests__ = [ RemoveCategoryWhenNotLogged, RemovePublicCategory,
			RemovePrivateCategory, RemoveOtherPlayerPrivateCategory ]

class CategoryTestSuite( TestSuite ):
	__name__  = 'Categories'
	__tests__ = [ GetCategoryTestSuite, GetCategoryIDsTestSuite, AddCategoryTestSuite, RemoveCategoryTestSuite ]

	def setUp( self ):
		Category = self.model.use( 'Category' )

		misc = Category(
				name = "Misc",
				description = "Things which dont fit into any other category." )

		production = Category(
				name = "Production",
				owner = self.ctx['players'][0],
				description = "Things which deal with the production of stuff." )

		combat = Category(
				name = "Combat",
				owner = self.ctx['players'][1],
				description = "Things which deal with combat between ships." )

		designs = Category(
				name = "Designs",
				description = "A category which has all the designs." )

		self.ctx['categories'] = [ misc, production, combat, designs ]

		Model.add( self.ctx['categories'] )
	
	def tearDown( self ):
		Model.remove( self.ctx['categories'] )

__tests__ = [ CategoryTestSuite ]
