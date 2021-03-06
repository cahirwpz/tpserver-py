from templates import ( AuthorizedTestSession, GetWithIDWhenNotLogged,
		GetIDSequenceWhenNotLogged, WhenNotLogged, GetItemWithID,
		WithIDTestMixin, GetItemIDs )
from testenv import GameTestEnvMixin

from tp.server.model import Model

class CategoryTestEnvMixin( GameTestEnvMixin ):
	def setUp( self ):
		Category = self.model.use( 'Category' )

		misc = Category(
				name = "Misc",
				description = "Things which dont fit into any other category." )

		production = Category(
				name = "Production",
				owner = self.players[0],
				description = "Things which deal with the production of stuff." )

		combat = Category(
				name = "Combat",
				owner = self.players[1],
				description = "Things which deal with combat between ships." )

		designs = Category(
				name = "Designs",
				description = "A category which has all the designs." )

		self.categories = [ misc, production, combat, designs ]

		Model.add( self.categories )
	
	def tearDown( self ):
		Model.remove( self.categories )

class GetCategoryMixin( WithIDTestMixin ):
	__request__  = 'GetCategory'
	__response__ = 'Category'

	__attrs__   = [ 'id', 'name', 'description' ]
	__attrmap__ = {}
	__attrfun__ = [ 'modtime' ]

class GetExistingCategory( GetItemWithID, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Does server respond properly if asked about existing category? """

	@property
	def item( self ):
		return self.categories[0]

class GetNonExistentCategory( GetItemWithID, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Does server fail to respond if asked about nonexistent category? """

	@property
	def item( self ):
		return self.categories[0]
	
	def getId( self, item ):
		return item.id + 666

	def getFail( self, item ):
		return 'NoSuchThing'

class GetPublicCategory( GetItemWithID, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Does server allow to fetch public Category? """

	@property
	def item( self ):
		return self.categories[3]

class GetPrivateCategory( GetItemWithID, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Does server allow to fetch private Category owned by the player? """

	@property
	def item( self ):
		return self.categories[1]

class GetOtherPlayerPrivateCategory( GetItemWithID, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Does server disallow to fetch private Category of another player? """

	@property
	def item( self ):
		return self.categories[2]

	def getFail( self, item ):
		return 'PermissionDenied'

class GetMultipleCategories( GetItemWithID, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Does server return sequence of Category packets if asked about two categories? """

	@property
	def items( self ):
		return [ self.categories[3], self.categories[0], self.categories[1] ]

class GetAllCategoryIDs( GetItemIDs, CategoryTestEnvMixin ):
	""" Does server return the IDs of all available Categories? """

	__request__  = 'GetCategoryIDs'
	__response__ = 'CategoryIDs'

	@property
	def items( self ):
		return [ self.categories[3], self.categories[0], self.categories[1] ]

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

class AddNewCategory( AuthorizedTestSession, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Is server able to add new category? """

	def __iter__( self ):
		AddCategory = self.protocol.use( 'AddCategory' )
		Category = self.model.use( 'Category' )

		response = yield AddCategory( self.seq, -1, 0, "Test", "Category for testing purposes." )

		self.assertPacket( response, 'Category' )

		self.cat = Category.ById( response.id )

		self.assertPacketEqual( response, self.cat )

	def tearDown( self ):
		if hasattr( self, 'cat' ):
			Model.remove( self.cat )

class AddCategoryButSameExists( AuthorizedTestSession, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Does server properly reject creating already existing private category? """

	def setUp( self ):
		self.cat_name = "Test"

		Category = self.model.use( 'Category' )

		self.cat = Category(
				name = self.cat_name,
				owner = self.players[0],
				description = "Private Category for testing purposes." )

		self.wrong_cat = None

		Model.add( self.cat )

	def __iter__( self ):
		AddCategory = self.protocol.use( 'AddCategory' )
		Category = self.model.use( 'Category' )

		response = yield AddCategory( self.seq, -1, 0, self.cat_name, "Category for testing purposes." )

		if response.type == 'Category':
			self.wrong_cat = Category.ById( response.id )

		self.assertPacketFail( response, 'PermissionDenied',
				"%s must not be added if %s exists!" % (self.wrong_cat, self.cat) )

	def tearDown( self ):
		Model.remove( getattr( self, 'cat', None ), getattr( self, 'wrong_cat', None ) )

class AddCategoryWithSameNameAsPrivate( AuthorizedTestSession, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Does server allow to add new category with same name but different player ? """

	def setUp( self ):
		self.cat_name = "Test"

		Category = self.model.use( 'Category' )

		self.other_cat = Category(
				name = self.cat_name,
				owner = self.players[1],
				description = "Private Category for testing purposes." )

		Model.add( self.other_cat )

	def __iter__( self ):
		AddCategory = self.protocol.use( 'AddCategory' )
		Category = self.model.use( 'Category' )

		response = yield AddCategory( self.seq, -1, 0, self.cat_name, "Category for testing purposes." )

		self.assertPacket( response, 'Category' )

		self.cat = Category.ById( response.id )

		self.assertPacketEqual( response, self.cat )

	def tearDown( self ):
		Model.remove( getattr( self, 'cat', None ), getattr( self, 'other_cat', None ) )

class AddCategoryWithSameNameAsPublic( AuthorizedTestSession, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Does server properly reject creating already existing private category with same name as a public one? """

	def setUp( self ):
		self.cat_name = "Test"

		Category = self.model.use( 'Category' )

		self.cat = Category(
				name = self.cat_name,
				description = "Public category for testing purposes." )

		self.wrong_cat = None

		Model.add( self.cat )

	def __iter__( self ):
		AddCategory = self.protocol.use( 'AddCategory' )
		Category = self.model.use( 'Category' )

		response = yield AddCategory( self.seq, -1, 0, self.cat_name, "Category for testing purposes." )

		if response.type == 'Category':
			self.wrong_cat = Category.ById( response.id )

		self.assertPacketFail( response, 'PermissionDenied',
				"%s must not be added if %s exists!" % (self.wrong_cat, self.cat) )

	def tearDown( self ):
		Model.remove( getattr( self, 'cat', None ), getattr( self, 'wrong_cat', None ) )

class RemoveCategoryWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got RemoveCategory request? """

	__request__ = 'RemoveCategory'

class RemovePublicCategory( AuthorizedTestSession, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Does server properly reject attempt to remove public category? """

	def setUp( self ):
		Category = self.model.use( 'Category' )

		self.cat = Category(
				name = "Public",
				description = "Public category for testing purposes." )

		Model.add( self.cat )

	def __iter__( self ):
		RemoveCategory = self.protocol.use( 'RemoveCategory' )

		response = yield RemoveCategory( self.seq, [ self.cat.id ] )

		self.assertPacketFail( response, 'PermissionDenied' )

	def tearDown( self ):
		Category = self.model.use( 'Category' )

		if Category.ById( self.cat.id ):
			Model.remove( self.cat )

		super( RemovePublicCategory, self ).tearDown()

class RemovePrivateCategory( AuthorizedTestSession, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Does server properly reject attempt to remove public category? """

	def setUp( self ):
		Category = self.model.use( 'Category' )

		self.cat = Category(
				name = "Private1",
				owner = self.players[0],
				description = "Private category for testing purposes." )

		Model.add( self.cat )

	def __iter__( self ):
		RemoveCategory = self.protocol.use( 'RemoveCategory' )

		response = yield RemoveCategory( self.seq, [ self.cat.id ] )

		self.assertPacket( response, 'Okay' )

	def tearDown( self ):
		Category = self.model.use( 'Category' )

		if Category.ById( self.cat.id ):
			Model.remove( self.cat )

class RemoveOtherPlayerPrivateCategory( AuthorizedTestSession, GetCategoryMixin, CategoryTestEnvMixin ):
	""" Does server properly reject attempt to remove other player's private category? """

	def setUp( self ):
		Category = self.model.use( 'Category' )

		self.cat = Category(
				name = "Private2",
				owner = self.players[1],
				description = "Private category for testing purposes." )

		Model.add( self.cat )

	def __iter__( self ):
		RemoveCategory = self.protocol.use( 'RemoveCategory' )

		response = yield RemoveCategory( self.seq, [ self.cat.id ] )

		self.assertPacketFail( response, 'PermissionDenied' )

	def tearDown( self ):
		Category = self.model.use( 'Category' )

		if Category.ById( self.cat.id ):
			Model.remove( self.cat )

__all__ = [	'GetExistingCategory', 
			'GetNonExistentCategory', 
			'GetPublicCategory', 
			'GetPrivateCategory', 
			'GetOtherPlayerPrivateCategory', 
			'GetMultipleCategories', 
			'GetAllCategoryIDs', 
			'GetCategoryWhenNotLogged', 
			'GetCategoryIDsWhenNotLogged', 
			'AddCategoryWhenNotLogged', 
			'AddNewCategory', 
			'AddCategoryButSameExists', 
			'AddCategoryWithSameNameAsPrivate', 
			'AddCategoryWithSameNameAsPublic', 
			'RemoveCategoryWhenNotLogged', 
			'RemovePublicCategory', 
			'RemovePrivateCategory', 
			'RemoveOtherPlayerPrivateCategory' ]
