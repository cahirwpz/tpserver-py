from templates import ( GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged,
		GetItemWithID, WithIDTestMixin, GetItemIDs )
from testenv import GameTestEnvMixin

from tp.server.model import Model

class ComponentTestEnvMixin( GameTestEnvMixin ):
	def setUp( self ):
		Component, ComponentProperty = self.model.use( 'Component', 'ComponentProperty' )
		Category, Property = self.model.use( 'Category', 'Property' )

		misc = Category(
				name = "Misc",
				description = "Things which dont fit into any other category." )

		ship = Category(
				name = "Ship",
				description = "Things which deal with ship's equipment." )

		combat = Category(
				name = "Combat",
				description = "Things which deal with combat between ships." )

		protection = Category(
				name = "Protection",
				description = "Things which deal with ship's protection." )

		self.categories = [ misc, ship, combat, protection ]

		speed = Property(
			categories   = [ ship ],
			name         = "speed",
			display_name = "Speed",
			description  = "The maximum number of parsecs the ship can move each turn.",
			calculate    = """(lambda (design) 1.0)""" )

		hp = Property(
			categories   = [ combat ],
			name         = "hp",
			display_name = "Hit Points",
			description  = "The amount of damage the ship can take.",
			calculate    = """(lambda (design) 1.0)""" )

		damage = Property(
			categories   = [ combat ],
			name         = "damage",
			display_name = "Damage",
			description  = "The amount of damage that the ship will do when using its weapon.",
			calculate    = """(lambda (design) 1.0)""" )

		escape = Property(
			categories   = [ ship ],
			name         = "escape",
			display_name = "Escape Chance",
			description  = "The chance the ship has of escaping from battle.",
			calculate    = """(lambda (design) 1.0)""" )

		self.properties = [ speed, hp, damage, escape ]

		missile = Component(
			id          = 9,
			name        = "Missile",
			description = "Missile which does 1HP of damage.",
			categories  = [ combat ],
			properties  = { 
				damage : """(lambda (design) 1.0)""",
				speed  : """(lambda (design) 1.0)""" })

		laser = Component(
			id          = 1,
			name        = "Laser",
			description = "Lasers which do 1HP of damage.",
			categories  = [ combat ],
			properties  = { damage : """(lambda (design) 1.0)""" })

		armor_plate = Component(
			id          = 4,
			name        = "Armor Plate",
			description = "Armor Plate which absorbes 1HP of damage.",
			categories  = [ ship, protection ] )

		primary_engine = Component(
			id          = 7,
			name        = "Primary Engine",
			description = "A part which allows a ship to move through space.",
			categories  = [ ship ],
			properties  = { speed : """(lambda (design) 1.0)""" })

		self.components = [ missile, laser, armor_plate, primary_engine ]

		Model.add( self.categories, self.properties, self.components )
	
	def tearDown( self ):
		Model.remove( self.components, self.properties, self.categories )

class GetComponentMixin( WithIDTestMixin ):
	__request__  = 'GetComponent'
	__response__ = 'Component'

	__attrs__   = [ 'id', 'name', 'description' ]
	__attrmap__ = {}
	__attrfun__ = [ 'modtime', 'categories', 'properties' ]

	def convert_categories( self, packet, obj ):
		return sorted( packet.categories ), sorted( cat.id for cat in obj.categories )

	def convert_properties( self, packet, obj ):
		return sorted( (prop[0], prop[1]) for prop in packet.properties ), \
				sorted( (prop.id, value) for prop, value in obj.properties.items() )

class GetComponentWhenNotLogged( GetWithIDWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetComponent request? """

	__request__ = 'GetComponent'

class GetExistingComponent( GetItemWithID, GetComponentMixin, ComponentTestEnvMixin ):
	""" Does server respond properly if asked about existing category? """

	@property
	def item( self ):
		return self.components[0]

class GetNonExistentComponent( GetItemWithID, GetComponentMixin, ComponentTestEnvMixin ):
	""" Does server fail to respond if asked about nonexistent category? """

	@property
	def item( self ):
		return self.components[0]
	
	def getId( self, item ):
		return item.id + 666

	def getFail( self, item ):
		return 'NoSuchThing'

class GetAllComponents( GetItemWithID, GetComponentMixin, ComponentTestEnvMixin ):
	""" Does server return sequence of Component packets if asked about all components? """

	@property
	def items( self ):
		return self.components

class GetComponentIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetComponentIDs request? """

	__request__ = 'GetComponentIDs'

class GetAllComponentIDs( GetItemIDs, ComponentTestEnvMixin ):
	""" Does server return the IDs of all available Components? """

	__request__  = 'GetComponentIDs'
	__response__ = 'ComponentIDs'

	@property
	def items( self ):
		return self.components

__all__ = [	'GetComponentWhenNotLogged', 
			'GetExistingComponent', 
			'GetNonExistentComponent', 
			'GetAllComponents', 
			'GetComponentIDsWhenNotLogged', 
			'GetAllComponentIDs' ]
