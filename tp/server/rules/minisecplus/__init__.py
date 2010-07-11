#!/usr/bin/env python

import os.path 

from tp.server.db import DatabaseManager

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
		from tp.server.rules.base.objects import Universe, Galaxy, StarSystem, Planet, Wormhole
		from tp.server.rules.minisec.objects import Fleet

		objs = self.game.objects

		Object, Player = objs.use( 'Object', 'Player' )

		objs.add_object_class( Universe )
		objs.add_object_class( Galaxy )
		objs.add_object_class( StarSystem )
		objs.add_object_class( Planet )
		objs.add_object_class( Fleet )
		objs.add_object_class( Wormhole )

		from tp.server.rules.base.parameters import ( AbsCoordParam, TimeParam,
				ObjectParam, PlayerParam, NumberParam, StringParam,
				ResourceCount, ResourceList, ResourceListParam, DesignCount,
				DesignList, DesignListParam )

		objs.add_class( ResourceCount, 'ResourceType' )
		objs.add_class( ResourceList, 'Parameter', 'ResourceCount' )

		objs.add_class( DesignCount, 'Design' )
		objs.add_class( DesignList, 'Parameter', 'DesignCount' )

		objs.add_parameter_class( AbsCoordParam )
		objs.add_parameter_class( TimeParam )
		objs.add_parameter_class( ObjectParam, 'Object' )
		objs.add_parameter_class( PlayerParam, 'Player' )
		objs.add_parameter_class( NumberParam )
		objs.add_parameter_class( StringParam )
		objs.add_parameter_class( DesignListParam )
		objs.add_parameter_class( ResourceListParam )

		# quick hack - to be removed
		objs.Object._row_type = objs.ObjectAttribute

	def createFleet( self, parent, name, owner = None):
		Fleet, DesignList, DesignCount, Design = self.game.objects.use( 'Fleet', 'DesignList', 'DesignCount', 'Design' )

		return Fleet(
			parent   = parent,
			size     = 3,
			name     = name,
			ships    = [ DesignList( design = DesignCount( design = Design.ByName('Frigate'), count = 3 ) ) ],
			position = parent.position,
			owner    = owner)

	def initialise( self ):
		Component, ComponentCategory, ComponentProperty		= self.game.objects.use( 'Component', 'ComponentCategory', 'ComponentProperty' )
		Category, Design, DesignCategory, DesignComponent	= self.game.objects.use( 'Category', 'Design', 'DesignCategory', 'DesignComponent' )
		Property, PropertyCategory, ResourceType		 	= self.game.objects.use( 'Property', 'PropertyCategory', 'ResourceType' )

		ResourceType.FromCSV( os.path.join( self.files, "resources.csv" ) )
		Category.FromCSV( os.path.join( self.files, "categories.csv" ) )

		misc       = Category.ByName('Misc')
		production = Category.ByName('Production')
		combat     = Category.ByName('Combat')

		universe = self.createUniverse( name = "The Universe" )

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

		with DatabaseManager().session() as session:
			session.add( universe )

			session.add( speed )
			session.add( cost )
			session.add( hp )
			session.add( backup_damage )
			session.add( primary_damage )
			session.add( escape )
			session.add( colonise )

			session.add( missile )
			session.add( laser )
			session.add( armor_plate )
			session.add( colonisation_pod )
			session.add( escape_thrusters )
			session.add( primary_engine )

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

		Object, ResourceCount, ResourceList, ResourceType = self.game.objects.use( 'Object', 'ResourceCount', 'ResourceList', 'ResourceType' )

		NaturalResourceTypes = [ ResourceType.ByName( name ) for name in [ 'Fruit Tree', 'Weird Artifact', 'Rock', 'Water' ] ]

		with DatabaseManager().session() as session:
			# Add a random smattering of resources to planets...
			for planet in Object.ByType('Planet'):
				for Type in self.random.sample( NaturalResourceTypes, self.random.randint(0, 4) ):
					planet.resources.append(
							ResourceList(
								resource = ResourceCount(
									type = Type,
									accessible   = self.random.randint( 0, 10 ),
									extractable  = self.random.randint( 0, 100 ),
									inaccessible = self.random.randint( 0, 1000 ))))

				session.add( planet )

	def player( self, username, password, email = 'Unknown', comment = 'A Minisec Player' ):
		"""
		Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
		"""

		user, system, planet, fleet = super( Ruleset, self ).player( username, password, email, comment )

		ResourceCount, ResourceList, ResourceType = self.game.objects.use( 'ResourceCount', 'ResourceList', 'ResourceType' )

		# Get the player's planet object and add the empire capital
		planet.resources = [
				ResourceList( resource = ResourceCount( type = ResourceType.ByName('House'), accessible = 1 ) ),
				ResourceList( resource = ResourceCount( type = ResourceType.ByName('Empire Capital'), accessible = 1 ) ) ]

		with DatabaseManager().session() as session:
			session.add( planet )
