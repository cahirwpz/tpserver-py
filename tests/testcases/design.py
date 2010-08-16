from test import TestSuite
from templates import ( GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged,
		WhenNotLogged, GetWithIDMixin, GetItemWithID, GetItemIDs,
		GetItemsWithID )

from tp.server.model import Model

class GetDesignMixin( GetWithIDMixin ):#{{{
	__request__  = 'GetDesign'
	__response__ = 'Design'

	__attrs__   = [ 'id', 'name', 'description' ]
	__attrmap__ = dict( feedback = "comment" )
	__attrfun__ = [ 'modtime', 'owner', 'categories', 'components', 'properties' ]

	def convert_owner( self, packet, obj ):
		pval = packet.owner if packet.owner != -1 else None
		oval = obj.owner_id

		return pval, oval

	def convert_categories( self, packet, obj ):
		return sorted( packet.categories ), sorted( cat.category_id for cat in obj.categories )

	def convert_properties( self, packet, obj ):
		return sorted( (prop[0], prop[1]) for prop in packet.properties ), \
				sorted( (prop.property_id, prop.value) for prop in obj.properties )

	def convert_components( self, packet, obj ):
		return sorted( (comp[0], comp[1]) for comp in packet.components ), \
				sorted( (comp.component_id, comp.amount) for comp in obj.components )
#}}}

class GetDesignWhenNotLogged( GetWithIDWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetDesign request? """

	__request__ = 'GetDesign'
#}}}

class GetExistingDesign( GetItemWithID, GetDesignMixin ):#{{{
	""" Does server respond properly if asked about existing board? """
	
	@property
	def item( self ):
		return self.ctx['designs'][1]
#}}}

class GetNonExistentDesign( GetItemWithID, GetDesignMixin ):#{{{
	""" Does server fail to respond if asked about nonexistent design? """

	__fail__ = 'NoSuchThing'

	@property
	def item( self ):
		return self.ctx['designs'][0]
	
	def getId( self, item ):
		return self.item.id + 666
#}}}

class GetMultipleDesigns( GetItemsWithID, GetDesignMixin ):#{{{
	""" Does server return the IDs of all available Designs? """

	@property
	def items( self ):
		return self.ctx['designs']
#}}}

class GetDesignIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetDesignIds request? """

	__request__ = 'GetDesignIDs'
#}}}

class GetAllDesignIDs( GetItemIDs ):#{{{
	""" Does server return the IDs of all available Designs? """

	__request__  = 'GetDesignIDs'
	__response__ = 'DesignIDs'
	__object__   = 'Design'

	@property
	def items( self ):
		return self.ctx['designs']
#}}}

class AddDesignWhenNotLogged( WhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got AddDesign request? """

	__request__ = 'AddDesign'

	def makeRequest( self, AddDesign ):
		return AddDesign( self.seq, 0, 0, [], "Design", "Design used for testing purposes", 0, 0, [], "foobar", [] )
#}}}

class ModifyDesignWhenNotLogged( WhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got ModifyDesign request? """

	__request__ = 'ModifyDesign'

	def makeRequest( self, ModifyDesign ):
		return ModifyDesign( self.seq, 0, 0, [], "Design", "Design used for testing purposes", 0, 0, [], "foobar", [] )
#}}}

class RemoveDesignWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got RemoveDesign request? """

	__request__ = 'RemoveDesign'
#}}}

class AddDesignTestSuite( TestSuite ):#{{{
	__name__  = 'AddDesign'
	__tests__ = [ AddDesignWhenNotLogged ]
#}}}

class GetDesignTestSuite( TestSuite ):#{{{
	__name__  = 'GetDesign'
	__tests__ = [ GetDesignWhenNotLogged, GetExistingDesign,
			GetNonExistentDesign, GetMultipleDesigns ]
#}}}

class GetDesignIDsTestSuite( TestSuite ):#{{{
	__name__  = 'GetDesignIDs'
	__tests__ = [ GetDesignIDsWhenNotLogged, GetAllDesignIDs ]
#}}}

class RemoveDesignTestSuite( TestSuite ):#{{{
	__name__  = 'RemoveDesign'
	__tests__ = [ RemoveDesignWhenNotLogged ]
#}}}

class ModifyDesignTestSuite( TestSuite ):#{{{
	__name__  = 'ModifyDesign'
	__tests__ = [ ModifyDesignWhenNotLogged ]
#}}}

class DesignTestSuite( TestSuite ):#{{{
	__name__  = 'Designs'
	__tests__ = [ AddDesignTestSuite, GetDesignTestSuite,
			GetDesignIDsTestSuite, RemoveDesignTestSuite,
			ModifyDesignTestSuite ]

	def setUp( self ):
		game = self.ctx['game']

		Component, ComponentCategory, ComponentProperty = self.model.use( 'Component', 'ComponentCategory', 'ComponentProperty' )
		Design, DesignCategory, DesignComponent, DesignProperty = self.model.use( 'Design', 'DesignCategory', 'DesignComponent', 'DesignProperty' )
		Category, Property, PropertyCategory = self.model.use( 'Category', 'Property', 'PropertyCategory' )

		misc = Category(
				name = "Misc",
				description = "Things which dont fit into any other category." )

		ship = Category(
				name = "Ship",
				description = "Things which deal with space ships." )

		combat = Category(
				name = "Combat",
				description = "Things which deal with combat between ships." )

		self.ctx['categories'] = [ misc, ship, combat ]

		experience = Property(
			categories   = [ PropertyCategory( category = misc ) ],
			name         = "experience",
			display_name = "XP",
			description  = "Experience points of a unit (gained in battles).",
			calculate    = "(lambda (design) (0))" )

		age = Property(
			categories   = [ PropertyCategory( category = misc ) ],
			name         = "age",
			display_name = "Turn",
			description  = "The age of a unit (in turns).",
			calculate    = "(lambda (design) (0))" )

		speed = Property(
			categories   = [ PropertyCategory( category = misc ) ],
			name         = "speed",
			display_name = "Speed",
			description  = "The maximum number of parsecs the ship can move each turn.",
			calculate    = "(lambda (design) (1.0))" )

		hp = Property(
			categories   = [ PropertyCategory( category = combat ) ],
			name         = "hp",
			display_name = "Hit Points",
			description  = "The amount of damage the ship can take.",
			calculate    = "(lambda (design) (1.0))" )

		backup_damage = Property(
			categories   = [ PropertyCategory( category = combat ) ],
			name         = "backup-damage",
			display_name = "Backup Damage",
			description  = "The amount of damage that the ship will do when using it's backup weapon. (IE When it draws a battle round.)",
			calculate    = "(lambda (design) (1.0))" )

		primary_damage = Property(
			categories   = [ PropertyCategory( category = combat ) ],
			name         = "primary-damage",
			display_name = "Primary Damage",
			description  = "The amount of damage that the ship will do when using it's primary weapon. (IE When it wins a battle round.)",
			calculate    = "(lambda (design) (1.0))" )

		escape = Property(
			categories   = [ PropertyCategory( category = ship ) ],
			name         = "escape",
			display_name = "Escape Chance",
			description  = "The chance the ship has of escaping from battle.",
			calculate    = "(lambda (design) (1.0))" )

		colonise = Property(
			categories   = [ PropertyCategory( category = ship ) ],
			name         = "colonise",
			display_name = "Can Colonise Planets",
			description  = "Can the ship colonise planets?",
			calculate    = """(lambda (design) ("Yes"))""" )

		self.ctx['properties'] = [ experience, age, speed, hp, backup_damage, primary_damage, escape, colonise ]

		missile = Component(
			name        = "Missile",
			description = "Missile which does 1HP of damage.",
			categories  = [ ComponentCategory( category = combat ) ],
			properties  = [ ComponentProperty( property = primary_damage ) ])

		laser = Component(
			name        = "Laser",
			description = "Lasers which do 1HP of damage.",
			categories  = [ ComponentCategory( category = combat ) ],
			properties  = [ ComponentProperty( property = backup_damage, value = """(lambda (design) 0.25)""" ) ])

		armor_plate = Component(
			name        = "Armor Plate",
			description = "Armor Plate which absorbes 1HP of damage.",
			categories  = [ ComponentCategory( category = combat) ],
			properties  = [ ComponentProperty( property = hp ) ])

		colonisation_pod = Component(
			name        = "Colonisation Pod",
			description = "A part which allows a ship to colonise a planet.",
			categories  = [ ComponentCategory( category = ship ) ],
			properties  = [ ComponentProperty( property = colonise ) ])

		escape_thrusters = Component(
			name        = "Escape Thrusters",
			description = "A part which allows a ship to escape combat.",
			categories  = [ ComponentCategory( category = ship ) ],
			properties  = [ ComponentProperty( property = escape, value = """(lambda (design) 0.25)""" ) ])

		primary_engine = Component(
			name        = "Primary Engine",
			description = "A part which allows a ship to move through space.",
			categories  = [ ComponentCategory( category = ship ) ],
			properties  = [ ComponentProperty( property = speed, value = """(lambda (design) 1000000)""" ) ])

		self.ctx['components'] = [ missile, laser, armor_plate, colonisation_pod, escape_thrusters, primary_engine ]

		scout = Design(
			name        = "Scout",
			description = "A fast light ship with advanced sensors.",
			comment     = "Send this ship to explore unknown solar systems.",
			categories  = [ DesignCategory( category = ship ) ],
			properties  = [ DesignProperty( property = age, value = "(lambda (design) 0)" ) ],
			components  = [
				DesignComponent( component = escape_thrusters, amount = 4 ),
				DesignComponent( component = armor_plate, amount = 2 ),
				DesignComponent( component = primary_engine, amount = 5 ) ])

		frigate = Design(
			name        = "Frigate",
			description = "A general purpose ship with weapons and ability to colonise new planets.",
			comment     = "Built it often and colonise every habitable planet you can!",
			categories  = [ DesignCategory( category = ship ) ],
			properties  = [
				DesignProperty( property = age, value = "(lambda (design) 0)" ),
				DesignProperty( property = experience, value = "(lambda (design) 0)" ) ],
			components  = [
				DesignComponent( component = armor_plate, amount = 4 ),
				DesignComponent( component = primary_engine, amount = 2 ),
				DesignComponent( component = colonisation_pod, amount = 1 ),
				DesignComponent( component = missile, amount = 2 ) ])

		battleship = Design(
			name        = "Battleship",
			description = "A heavy ship which main purpose is to crush the other ships.",
			comment     = "This is really a powerful ship!",
			categories  = [ DesignCategory( category = ship ) ],
			properties  = [
				DesignProperty( property = age, value = "(lambda (design) 0)" ),
				DesignProperty( property = experience, value = "(lambda (design) 0)" ) ],
			components  = [
				DesignComponent( component = armor_plate, amount = 6 ),
				DesignComponent( component = primary_engine, amount = 3 ),
				DesignComponent( component = missile, amount = 3 ),
				DesignComponent( component = laser, amount = 4 ) ])

		self.ctx['designs'] = [ scout, frigate, battleship ]

		Model.add( self.ctx['categories'], self.ctx['properties'],
				self.ctx['components'], self.ctx['designs'] )
	
	def tearDown( self ):
		Model.remove( self.ctx['designs'], self.ctx['components'],
				self.ctx['properties'], self.ctx['categories'] )
#}}}

__tests__ = [ DesignTestSuite ]
