from test import TestSuite
from templates import GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged, GetItemsWithID, GetWithIDMixin, GetItemIDs

from tp.server.model import Model

class GetPropertyMixin( GetWithIDMixin ):#{{{
	__request__  = 'GetProperty'
	__response__ = 'Property'

	__attrs__ = [ 'id', 'name', 'description' ]

	__attrmap__ = dict(
			displayname = "display_name",
			calculatefunc =	"calculate",
			requirementfunc = "requirements" )

	__attrfun__ = [ 'modtime', 'categories' ]

	def convert_categories( self, packet, obj ):
		return sorted( packet.categories ), sorted( cat.category_id for cat in obj.categories )
#}}}

class GetPropertyWhenNotLogged( GetWithIDWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetProperty request? """

	__request__ = 'GetProperty'
#}}}

class GetAllProperties( GetItemsWithID, GetPropertyMixin ):#{{{
	""" Does server return sequence of Property packets if asked about all properties? """

	@property
	def items( self ):
		return reversed( self.ctx['properties'] )
#}}}

class GetPropertyIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetPropertyIDs request? """

	__request__ = 'GetPropertyIDs'
#}}}

class GetAllPropertyIDs( GetItemIDs ):#{{{
	""" Does server return the IDs of all available Properties? """

	__request__  = 'GetPropertyIDs'
	__response__ = 'PropertyIDs'
	__object__   = 'Property'

	@property
	def items( self ):
		return self.ctx['properties']
#}}}

class PropertiesTestSuite( TestSuite ):#{{{
	""" Performs all tests related to GetProperty and GetPropertyIDs requests. """
	__name__  = 'Properties'
	__tests__ = [ GetPropertyWhenNotLogged, GetAllProperties, GetPropertyIDsWhenNotLogged, GetAllPropertyIDs ]

	def setUp( self ):
		game = self.ctx['game']

		Property, PropertyCategory, Category = game.objects.use( 'Property', 'PropertyCategory', 'Category' )

		misc = Category(
				id = 7,
				name = "Misc",
				description = "Things which dont fit into any other category." )

		production = Category(
				id = 16,
				name = "Production",
				description = "Things which deal with the production of stuff." )

		combat = Category(
				id = 3,
				name = "Combat",
				description = "Things which deal with combat between ships." )

		designs = Category(
				id = 12,
				name = "Designs",
				description = "A category which has all the designs." )

		speed = Property(
			id           = 10,
			categories   = [ PropertyCategory( category = misc ), PropertyCategory( category = designs ) ],
			name         = "speed",
			display_name = "Speed",
			description  = "The maximum number of parsecs the ship can move each turn.",
			calculate    = "" )

		cost = Property(
			id           = 13,
			categories   = [ PropertyCategory( category = production ) ],
			name         = "cost",
			display_name = "Cost",
			description  = "The number of components needed to build the ship",
			calculate    = "" )

		hp = Property(
			id           = 4,
			categories   = [ PropertyCategory( category = combat ) ],
			name         = "hp",
			display_name = "Hit Points",
			description  = "The amount of damage the ship can take.",
			calculate    = "" )

		backup_damage = Property(
			id           = 7,
			categories   = [ PropertyCategory( category = combat ) ],
			name         = "backup-damage",
			display_name = "Backup Damage",
			description  = "The amount of damage that the ship will do when using it's backup weapon. (IE When it draws a battle round.)",
			calculate    = "" )

		primary_damage = Property(
			id           = 2,
			categories   = [ PropertyCategory( category = combat ) ],
			name         = "primary-damage",
			display_name = "Primary Damage",
			description  = "The amount of damage that the ship will do when using it's primary weapon. (IE When it wins a battle round.)",
			calculate    = "" )

		escape = Property(
			id           = 9,
			categories   = [ PropertyCategory( category = misc ), PropertyCategory( category = designs ) ],
			name         = "escape",
			display_name = "Escape Chance",
			description  = "The chance the ship has of escaping from battle.",
			calculate    = "" )

		colonise = Property(
			id           = 99,
			categories   = [ PropertyCategory( category = misc ), PropertyCategory( category = designs ) ],
			name         = "colonise",
			display_name = "Can Colonise Planets",
			description  = "Can the ship colonise planets?",
			calculate    = "" )

		self.ctx['categories'] = [ misc, production, combat, designs ]
		self.ctx['properties'] = [ speed, cost, hp, backup_damage, primary_damage, escape, colonise ]

		Model.add( self.ctx['categories'], self.ctx['properties'] )
	
	def tearDown( self ):
		Model.remove( self.ctx['properties'], self.ctx['categories'] )
#}}}

__tests__ = [ PropertiesTestSuite ]
