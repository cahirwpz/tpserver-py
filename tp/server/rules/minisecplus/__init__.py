#!/usr/bin/env python

import os.path 

from tp.server.db import DatabaseManager, make_dependant_mapping, make_parametrized_mapping

from tp.server.rules.minisec import Ruleset as MinisecRuleset

class Ruleset( MinisecRuleset ):
	"""
	Minisec+ Ruleset.

	This ruleset exploits extra features introduced after Minisec was designed
	(such as Designs and Resources) while still remaining as close to Minisec
	as possible.
	"""
	name = "Minisec+"
	version = "0.0.1"

	files = os.path.join(os.path.dirname( __file__ ), "other")

	def load( self ):
		metadata = DatabaseManager().metadata

		from tp.server.bases.objects import UniverseClass, GalaxyClass, StarSystemClass, PlanetClass, WormholeClass
		from tp.server.rules.minisec.objects import Resource, FleetClass, FleetComposition

		game = self.game

		Object = game.Object

		game.Universe			= make_parametrized_mapping( UniverseClass( Object ),	metadata, Object )
		game.Galaxy   			= make_parametrized_mapping( GalaxyClass( Object ),		metadata, Object )
		game.StarSystem			= make_parametrized_mapping( StarSystemClass( Object ),	metadata, Object )
		game.Planet				= make_parametrized_mapping( PlanetClass( Object ),		metadata, Object, game.Player )
		game.Fleet				= make_parametrized_mapping( FleetClass( Object ),		metadata, Object, game.Player )
		game.Wormhole			= make_parametrized_mapping( WormholeClass( Object ),	metadata, Object )
		game.FleetComposition	= make_dependant_mapping( FleetComposition, metadata, game, game.Fleet, game.Design )
		game.Resource			= make_dependant_mapping( Resource, metadata, game, game.Object, game.ResourceType )

	def createFleet( self, parent, name, owner = None):
		fleet = self.game.Fleet()
		fleet.parent   = parent
		fleet.size     = 3
		fleet.name     = name
		fleet.ships    = [ self.game.FleetComposition( ship = self.game.Design.ByName('Frigate'), number = 3 ) ]
		fleet.position = parent.position
		fleet.owner    = owner

		return fleet

	def initialise( self ):
		Category          = self.game.Category
		Component         = self.game.Component
		ComponentCategory = self.game.ComponentCategory
		ComponentProperty = self.game.ComponentProperty
		Design            = self.game.Design
		DesignCategory    = self.game.DesignCategory
		DesignComponent   = self.game.DesignComponent
		Property          = self.game.Property
		PropertyCategory  = self.game.PropertyCategory
		ResourceType      = self.game.ResourceType

		ResourceType.FromCSV( os.path.join( self.files, "resources.csv" ) )
		Category.FromCSV( os.path.join( self.files, "categories.csv" ) )

		misc       = Category.ByName('Misc')
		production = Category.ByName('Production')
		combat     = Category.ByName('Combat')

		with DatabaseManager().session() as session:
			universe = self.createUniverse( name = "The Universe" )

			session.add( universe )

			speed = Property(
				categories   = [ PropertyCategory( category = misc ) ],
				name         = "speed",
				display_name = "Speed",
				description  = "The maximum number of parsecs the ship can move each turn.",
				calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits)))
		(cons n (string-append (number->string (/ n 1000000)) " kpcs"))))""" )

			cost = Property(
				categories   = [ PropertyCategory( category = production ) ],
				name         = "cost",
				display_name = "Cost",
				description  = "The number of components needed to build the ship",
				calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) " turns"))))""" )

			hp = Property(
				categories   = [ PropertyCategory( category = combat ) ],
				name         = "hp",
				display_name = "Hit Points",
				description  = "The amount of damage the ship can take.",
				calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) " HP"))))""" )

			backup_damage = Property(
				categories   = [ PropertyCategory( category = combat ) ],
				name         = "backup-damage",
				display_name = "Backup Damage",
				description  = "The amount of damage that the ship will do when using it's backup weapon. (IE When it draws a battle round.)",
				calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) " HP"))))""" )

			primary_damage = Property(
				categories   = [ PropertyCategory( category = combat ) ],
				name         = "primary-damage",
				display_name = "Primary Damage",
				description  = "The amount of damage that the ship will do when using it's primary weapon. (IE When it wins a battle round.)",
				calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) " HP"))))""" )

			escape = Property(
				categories   = [ PropertyCategory( category = misc ) ],
				name         = "escape",
				display_name = "Escape Chance",
				description  = "The chance the ship has of escaping from battle.",
				calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string (* n 100)) " %"))))""" )

			colonise = Property(
				categories   = [ PropertyCategory( category = misc ) ],
				name         = "colonise",
				display_name = "Can Colonise Planets",
				description  = "Can the ship colonise planets?",
				calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n 
			(if (> n 1) "Yes" "No"))))""" )

			session.add( speed )
			session.add( cost )
			session.add( hp )
			session.add( backup_damage )
			session.add( primary_damage )
			session.add( escape )
			session.add( colonise )

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
				categories  = [ ComponentCategory( category = misc ) ],
				properties  = [ ComponentProperty( property = colonise ) ])

			escape_thrusters = Component(
				name        = "Escape Thrusters",
				description = "A part which allows a ship to escape combat.",
				categories  = [ ComponentCategory( category = misc ) ],
				properties  = [ ComponentProperty( property = escape, value = """(lambda (design) 0.25)""" ) ])

			primary_engine = Component(
				name        = "Primary Engine",
				description = "A part which allows a ship to move through space.",
				categories  = [ ComponentCategory( category = misc ) ],
				properties  = [ ComponentProperty( property = speed, value = """(lambda (design) 1000000)""" ) ])

			session.add( missile )
			session.add( laser )
			session.add( armor_plate )
			session.add( colonisation_pod )
			session.add( escape_thrusters )
			session.add( primary_engine )

			scout = Design(
				name        = "Scout",
				description = "A fast light ship with advanced sensors.",
				categories  = [ DesignCategory( category = misc ) ],
				components  = [
					DesignComponent( component = escape_thrusters, amount = 4 ),
					DesignComponent( component = armor_plate, amount = 2 ),
					DesignComponent( component = primary_engine, amount = 5 ) ])
	
			frigate = Design(
				name         = "Frigate",
				description  = "A general purpose ship with weapons and ability to colonise new planets.",
				categories   = [ DesignCategory( category = misc ) ],
				components   = [
					DesignComponent( component = armor_plate, amount = 4 ),
					DesignComponent( component = primary_engine, amount = 2 ),
					DesignComponent( component = colonisation_pod, amount = 1 ),
					DesignComponent( component = missile, amount = 2 ) ])

			battleship = Design(
				name        = "Battleship",
				description = "A heavy ship who's main purpose is to blow up other ships.",
				categories  = [ DesignCategory( category = misc ) ],
				components  = [
					DesignComponent( component = armor_plate, amount = 6 ),
					DesignComponent( component = primary_engine, amount = 3 ),
					DesignComponent( component = missile, amount = 3 ),
					DesignComponent( component = laser, amount = 4 ) ])

			session.add( scout )
			session.add( frigate )
			session.add( battleship )

			# FIXME: Need to populate the database with the MiniSec design stuff,
			#  - Firepower
			#  - Armor/HP
			#  - Speed
			#  - Sensors (scouts ability to disappear)....

	def populate( self, seed, system_min, system_max, planet_min, planet_max ):
		"""
		--populate <game> <random seed> <min systems> <max systems> <min planets> <max planets>
		
			Populate a universe with a number of systems and planets.
			The number of systems in the universe is dictated by min/max systems.
			The number of planets per system is dictated by min/max planets.
		"""
		super( Ruleset, self ).populate(seed, system_min, system_max, planet_min, planet_max)

		Object       = self.game.Object
		Resource     = self.game.Resource
		ResourceType = self.game.ResourceType

		NaturalResourceTypes = [ ResourceType.ByName( name ) for name in [ 'Fruit Tree', 'Weird Artifact', 'Rock', 'Water' ] ]

		with DatabaseManager().session() as session:
			# Add a random smattering of resources to planets...
			for planet in Object.ByType('Planet'):
				Types = self.random.sample( NaturalResourceTypes, self.random.randint(0, 4) )

				for Type in Types:
					planet.resources.append( Resource( type = Type,
						accessible   = self.random.randint( 0, 10 ),
						extractable  = self.random.randint( 0, 100 ),
						inaccessible = self.random.randint( 0, 1000 )) )

				session.add( planet )

	def player( self, username, password, email = 'Unknown', comment = 'A Minisec Player' ):
		"""
		Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
		"""

		user, system, planet, fleet = super( Ruleset, self ).player( username, password, email, comment )

		ResourceType = self.game.ResourceType

		house   = ResourceType.ByName('House')
		capital = ResourceType.ByName('Empire Capital')

		with DatabaseManager().session() as session:
			# Get the player's planet object and add the empire capital

			planet.resources = [
					self.game.Resource( type = house, accessible = 1 ),
					self.game.Resource( type = capital, accessible = 1 ) ]

			session.add( planet )
