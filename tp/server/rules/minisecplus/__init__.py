#!/usr/bin/env python

import os.path 

from tp.server.model import Model
from tp.server.rules.base import Ruleset
from tp.server.rules.minisec import MinisecRuleset, MinisecUniverseGenerator

class MinisecPlusUniverseGenerator( MinisecUniverseGenerator ):
	def createFleet( self, parent, name, owner = None):
		Fleet, Design = self.model.use( 'Fleet', 'Design' )

		return Fleet(
			parent   = parent,
			size     = 3,
			name     = name,
			ships    = { Design.ByName('Frigate') : 3 },
			position = parent.position,
			owner    = owner)
	
	def addResourcesToPlanet( self, planet ):
		ResourceType = self.model.use( 'ResourceType' )

		NaturalResourceTypes = [ ResourceType.ByName( name ) for name in [ 'Fruit Tree', 'Weird Artifact', 'Rock', 'Water' ] ]

		# Add a random smattering of resources to planets...
		for Type in self.random.sample( NaturalResourceTypes, self.randint(0, 4) ):
			planet.resources[ Type ] = {
					'accessible'   : self.randint( 0, 10 ),
					'extractable'  : self.randint( 0, 100 ),
					'inaccessible' : self.randint( 0, 1000 ) }

		Model.update( planet )

class MinisecPlusRuleset( MinisecRuleset ):
	"""
	Minisec+ Ruleset.

	This ruleset exploits extra features introduced after Minisec was designed
	(such as Designs and Resources) while still remaining as close to Minisec
	as possible.
	"""
	name    = "minisecplus"
	version = "0.0.1"

	RulesetUniverseGeneratorClass = MinisecPlusUniverseGenerator

	files = os.path.join( os.path.dirname( __file__ ), "other" )

	def loadModel( self ):
		Ruleset.loadModel( self )

	def initModel( self ):
		Ruleset.initModel( self )

		Category, Property, ResourceType = self.model.use( 'Category', 'Property', 'ResourceType' )
		Component, ComponentProperty     = self.model.use( 'Component', 'ComponentProperty' )
		Design, DesignComponent          = self.model.use( 'Design', 'DesignComponent' )

		ResourceType.FromCSV( os.path.join( self.files, "resources.csv" ) )
		Category.FromCSV( os.path.join( self.files, "categories.csv" ) )

		misc       = Category.ByName('Misc')
		production = Category.ByName('Production')
		combat     = Category.ByName('Combat')

		universe = self.generator.createUniverse( name = "The Universe" )

		speed = Property(
			categories   = [ misc ],
			name         = "speed",
			display_name = "Speed",
			description  = "The maximum number of parsecs the ship can move each turn.",
			calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits)))
		(cons n (string-append (number->string (/ n 1000000)) " kpcs"))))""" )

		cost = Property(
			categories   = [ production ],
			name         = "cost",
			display_name = "Cost",
			description  = "The number of components needed to build the ship",
			calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) " turns"))))""" )

		hp = Property(
			categories   = [ combat ],
			name         = "hp",
			display_name = "Hit Points",
			description  = "The amount of damage the ship can take.",
			calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) " HP"))))""" )

		backup_damage = Property(
			categories   = [ combat ],
			name         = "backup-damage",
			display_name = "Backup Damage",
			description  = "The amount of damage that the ship will do when using it's backup weapon. (IE When it draws a battle round.)",
			calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) " HP"))))""" )

		primary_damage = Property(
			categories   = [ combat ],
			name         = "primary-damage",
			display_name = "Primary Damage",
			description  = "The amount of damage that the ship will do when using it's primary weapon. (IE When it wins a battle round.)",
			calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) " HP"))))""" )

		escape = Property(
			categories   = [ misc ],
			name         = "escape",
			display_name = "Escape Chance",
			description  = "The chance the ship has of escaping from battle.",
			calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string (* n 100)) " %"))))""" )

		colonise = Property(
			categories   = [ misc ],
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
			categories  = [ misc ],
			properties  = { colonise : None })

		escape_thrusters = Component(
			name        = "Escape Thrusters",
			description = "A part which allows a ship to escape combat.",
			categories  = [ misc ],
			properties  = { escape : """(lambda (design) 0.25)""" })

		primary_engine = Component(
			name        = "Primary Engine",
			description = "A part which allows a ship to move through space.",
			categories  = [ misc ],
			properties  = { speed : """(lambda (design) 1000000)""" })

		scout = Design(
			name        = "Scout",
			description = "A fast light ship with advanced sensors.",
			categories  = [ misc ],
			components  = {
				escape_thrusters : 4,
				armor_plate      : 2,
				primary_engine   : 5 })

		frigate = Design(
			name         = "Frigate",
			description  = "A general purpose ship with weapons and ability to colonise new planets.",
			categories   = [ misc ],
			components   = {
				armor_plate      : 4,
				primary_engine   : 2,
				colonisation_pod : 1,
				missile          : 2 })

		battleship = Design(
			name        = "Battleship",
			description = "A heavy ship who's main purpose is to blow up other ships.",
			categories  = [ misc ],
			components  = {
				armor_plate    : 6,
				primary_engine : 3,
				missile        : 3,
				laser          : 4 })

		# FIXME: Need to populate the database with the MiniSec design stuff,
		#  - Firepower
		#  - Armor/HP
		#  - Speed
		#  - Sensors (scouts ability to disappear)....

		Model.add( universe, speed, cost, hp, backup_damage, primary_damage,
				escape, colonise, missile, laser, armor_plate,
				colonisation_pod, escape_thrusters, primary_engine, scout,
				frigate, battleship)

	def populate( self, *args ):
		"""
		Populate a universe with a number of systems and planets.
		"""
		MinisecRuleset.populate( self, *args )

		Object = self.model.use( 'Object' )

		for planet in Object.ByType('Planet'):
			self.generator.addResourcesToPlanet( planet )

	def addPlayer( self, username, password, email = 'Unknown', comment = 'A Minisec Player' ):
		"""
		Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
		"""
		user, system, planet, fleet = MinisecRuleset.addPlayer( self, username, password, email, comment )

		ResourceType = self.model.use( 'ResourceType' )

		# Get the player's planet object and add the empire capital
		planet.resources = { 
				ResourceType.ByName('House')          : { 'accessible' : 1 },
				ResourceType.ByName('Empire Capital') : { 'accessible' : 1 } }

		Model.update( planet )

__all__ = [ 'MinisecPlusRuleset' ]
