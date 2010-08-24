from templates import ( GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged,
		WhenNotLogged, WithIDTestMixin, GetItemWithID, GetItemIDs )

from testenv import GameTestEnvMixin

from tp.server.model import Model

class DesignTestEnvMixin( GameTestEnvMixin ):
	def setUp( self ):
		Component, ComponentProperty = self.model.use( 'Component', 'ComponentProperty' )
		Design, DesignComponent, DesignProperty = self.model.use( 'Design', 'DesignComponent', 'DesignProperty' )
		Category, Property = self.model.use( 'Category', 'Property' )

		misc = Category(
				name = "Misc",
				description = "Things which dont fit into any other category." )

		ship = Category(
				name = "Ship",
				description = "Things which deal with space ships." )

		combat = Category(
				name = "Combat",
				description = "Things which deal with combat between ships." )

		self.categories = [ misc, ship, combat ]

		experience = Property(
			categories   = [ misc ],
			name         = "experience",
			display_name = "XP",
			description  = "Experience points of a unit (gained in battles).",
			calculate    = "(lambda (design) (0))" )

		age = Property(
			categories   = [ misc ],
			name         = "age",
			display_name = "Turn",
			description  = "The age of a unit (in turns).",
			calculate    = "(lambda (design) (0))" )

		speed = Property(
			categories   = [ misc ],
			name         = "speed",
			display_name = "Speed",
			description  = "The maximum number of parsecs the ship can move each turn.",
			calculate    = "(lambda (design) (1.0))" )

		hp = Property(
			categories   = [ combat ],
			name         = "hp",
			display_name = "Hit Points",
			description  = "The amount of damage the ship can take.",
			calculate    = "(lambda (design) (1.0))" )

		backup_damage = Property(
			categories   = [ combat ],
			name         = "backup-damage",
			display_name = "Backup Damage",
			description  = "The amount of damage that the ship will do when using it's backup weapon. (IE When it draws a battle round.)",
			calculate    = "(lambda (design) (1.0))" )

		primary_damage = Property(
			categories   = [ combat ],
			name         = "primary-damage",
			display_name = "Primary Damage",
			description  = "The amount of damage that the ship will do when using it's primary weapon. (IE When it wins a battle round.)",
			calculate    = "(lambda (design) (1.0))" )

		escape = Property(
			categories   = [ ship ],
			name         = "escape",
			display_name = "Escape Chance",
			description  = "The chance the ship has of escaping from battle.",
			calculate    = "(lambda (design) (1.0))" )

		colonise = Property(
			categories   = [ ship ],
			name         = "colonise",
			display_name = "Can Colonise Planets",
			description  = "Can the ship colonise planets?",
			calculate    = """(lambda (design) ("Yes"))""" )

		self.properties = [ experience, age, speed, hp, backup_damage, primary_damage, escape, colonise ]

		missile = Component(
			name        = "Missile",
			description = "Missile which does 1HP of damage.",
			categories  = [ combat ],
			properties  = { primary_damage : None })

		laser = Component(
			name        = "Laser",
			description = "Lasers which do 1HP of damage.",
			categories  = [ combat ],
			properties  = { backup_damage : """(lambda (design) 0.25)""" })

		armor_plate = Component(
			name        = "Armor Plate",
			description = "Armor Plate which absorbes 1HP of damage.",
			categories  = [ combat ],
			properties  = { hp : None })

		colonisation_pod = Component(
			name        = "Colonisation Pod",
			description = "A part which allows a ship to colonise a planet.",
			categories  = [ ship ],
			properties  = { colonise : None })

		escape_thrusters = Component(
			name        = "Escape Thrusters",
			description = "A part which allows a ship to escape combat.",
			categories  = [ ship ],
			properties  = { escape : """(lambda (design) 0.25)""" })

		primary_engine = Component(
			name        = "Primary Engine",
			description = "A part which allows a ship to move through space.",
			categories  = [ ship ],
			properties  = { speed : """(lambda (design) 1000000)""" })

		self.components = [ missile, laser, armor_plate, colonisation_pod, escape_thrusters, primary_engine ]

		scout = Design(
			name        = "Scout",
			description = "A fast light ship with advanced sensors.",
			comment     = "Send this ship to explore unknown solar systems.",
			categories  = [ ship ],
			properties  = { age : "(lambda (design) 0)" },
			components  = {
				escape_thrusters : 4,
				armor_plate      : 2,
				primary_engine   : 5 })

		frigate = Design(
			name        = "Frigate",
			description = "A general purpose ship with weapons and ability to colonise new planets.",
			comment     = "Built it often and colonise every habitable planet you can!",
			categories  = [ ship ],
			properties  = {
				age        : "(lambda (design) 0)",
				experience : "(lambda (design) 0)" },
			components  = {
				armor_plate      : 4,
				primary_engine   : 2,
				colonisation_pod : 1,
				missile          : 2 })

		battleship = Design(
			name        = "Battleship",
			description = "A heavy ship which main purpose is to crush the other ships.",
			comment     = "This is really a powerful ship!",
			categories  = [ ship ],
			properties  = {
				age        : "(lambda (design) 0)",
				experience : "(lambda (design) 0)" },
			components  = {
				armor_plate    : 6,
				primary_engine : 3,
				missile        : 3,
				laser          : 4 })

		self.designs = [ scout, frigate, battleship ]

		Model.add( self.categories, self.properties,
				self.components, self.designs )
	
	def tearDown( self ):
		Model.remove( self.designs, self.components,
				self.properties, self.categories )

class GetDesignMixin( WithIDTestMixin ):
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
		return sorted( packet.categories ), sorted( cat.id for cat in obj.categories )

	def convert_properties( self, packet, obj ):
		return sorted( (prop[0], prop[1]) for prop in packet.properties ), \
				sorted( (prop.id, value) for prop, value in obj.properties.items() )

	def convert_components( self, packet, obj ):
		return sorted( (comp[0], comp[1]) for comp in packet.components ), \
				sorted( (comp.id, amount) for comp, amount in obj.components.items() )

class GetDesignWhenNotLogged( GetWithIDWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetDesign request? """

	__request__ = 'GetDesign'

class GetExistingDesign( GetItemWithID, GetDesignMixin, DesignTestEnvMixin ):
	""" Does server respond properly if asked about existing board? """
	
	@property
	def item( self ):
		return self.designs[1]

class GetNonExistentDesign( GetItemWithID, GetDesignMixin, DesignTestEnvMixin ):
	""" Does server fail to respond if asked about nonexistent design? """

	@property
	def item( self ):
		return self.designs[0]
	
	def getId( self, item ):
		return item.id + 666

	def getFail( self, item ):
		return 'NoSuchThing'

class GetMultipleDesigns( GetItemWithID, GetDesignMixin, DesignTestEnvMixin ):
	""" Does server return the IDs of all available Designs? """

	@property
	def items( self ):
		return self.designs

class GetDesignIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetDesignIds request? """

	__request__ = 'GetDesignIDs'

class GetAllDesignIDs( GetItemIDs, DesignTestEnvMixin ):
	""" Does server return the IDs of all available Designs? """

	__request__  = 'GetDesignIDs'
	__response__ = 'DesignIDs'

	@property
	def items( self ):
		return self.designs

class AddDesignWhenNotLogged( WhenNotLogged ):
	""" Does a server respond properly when player is not logged but got AddDesign request? """

	__request__ = 'AddDesign'

	def makeRequest( self, AddDesign ):
		return AddDesign( self.seq, 0, 0, [], "Design", "Design used for testing purposes", 0, 0, [], "foobar", [] )

class ModifyDesignWhenNotLogged( WhenNotLogged ):
	""" Does a server respond properly when player is not logged but got ModifyDesign request? """

	__request__ = 'ModifyDesign'

	def makeRequest( self, ModifyDesign ):
		return ModifyDesign( self.seq, 0, 0, [], "Design", "Design used for testing purposes", 0, 0, [], "foobar", [] )

class RemoveDesignWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got RemoveDesign request? """

	__request__ = 'RemoveDesign'

__all__ = [	'GetDesignWhenNotLogged', 
			'GetExistingDesign', 
			'GetNonExistentDesign', 
			'GetMultipleDesigns', 
			'GetDesignIDsWhenNotLogged', 
			'GetAllDesignIDs', 
			'AddDesignWhenNotLogged', 
			'ModifyDesignWhenNotLogged', 
			'RemoveDesignWhenNotLogged' ]
