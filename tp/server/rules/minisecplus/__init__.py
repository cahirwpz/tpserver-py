
import os.path
import csv
import random
import pprint

from tp.server.db import dbconn, convert

from tp.server.bases.Object    import Object
from tp.server.bases.Resource  import Resource
from tp.server.bases.Category  import Category
from tp.server.bases.Property  import Property
from tp.server.bases.Component import Component
from tp.server.bases.Design    import Design

from tp.server.rules.base.objects import Planet
from tp.server.rules.minisec      import Ruleset as MinisecRuleset


class Ruleset(MinisecRuleset):
	"""
	Minisec+ Ruleset.

	This ruleset exploits extra features introduced after Minisec was designed
	(such as Designs and Resources) while still remaining as close to Minisec
	as possible.
	"""
	name = "Minisec+"
	version = "0.0.1"

	files = os.path.join(os.path.dirname(__file__), "other")

	def initalise(self, seed=None):
		"""\
		Minisec 
		"""

		dbconn.use(self.game)

		trans = dbconn.begin()
		try:
			MinisecRuleset.initalise(self)

			reader = csv.DictReader(open(os.path.join(self.files, "resources.csv"), "r"))
			for row in reader:
				r = Resource()
				for name, cell in row.iteritems():
					if cell is '':
						continue
					setattr(r, name, convert(getattr(Resource.table.c, name), cell))

				pprint.pprint(r.__dict__)

				r.insert()


			reader = csv.DictReader(open(os.path.join(self.files, "categories.csv"), "r"))
			for row in reader:
				c = Category()
				for name, cell in row.iteritems():
					setattr(c, name, cell)

				pprint.pprint(c.__dict__)

				c.insert()

			# Create the properties that a design might have
			p = Property()
			p.categories = [Category.byname('Misc')]
			p.name = "speed"
			p.displayname = "Speed"
			p.desc = "The maximum number of parsecs the ship can move each turn."
			p.calculate   = """\
(lambda (design bits) 
	(let ((n (apply + bits)))
		(cons n (string-append (number->string (/ n 1000000)) " kpcs"))))
"""
			p.insert()
 
			p = Property()
			p.categories = [Category.byname('Production')]
			p.name = "cost"
			p.displayname = "Cost"
			p.desc = "The number of components needed to build the ship"
			p.calculate   = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) " turns")) ) )
"""
			p.insert()
	
			p = Property()
			p.categories = [Category.byname('Combat')]
			p.name = "hp"
			p.displayname = "Hit Points"
			p.desc = "The amount of damage the ship can take."
			p.calculate   = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) " HP"))))
"""
			p.insert()
	
			p = Property()
			p.categories = [Category.byname('Combat')]
			p.name = "backup-damage"
			p.displayname = "Backup Damage"
			p.desc = "The amount of damage that the ship will do when using it's backup weapon. (IE When it draws a battle round.)"
			p.calculate   = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) " HP"))))
"""
			p.insert()
	
			p = Property()
			p.categories = [Category.byname('Combat')]
			p.name = "primary-damage"
			p.displayname = "Primary Damage"
			p.desc = "The amount of damage that the ship will do when using it's primary weapon. (IE When it wins a battle round.)"
			p.calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string n) " HP"))))
"""
			p.insert()

			p = Property()
			p.categories = [Category.byname('Misc')]
			p.name = "escape"
			p.displayname = "Escape Chance"
			p.desc = "The chance the ship has of escaping from battle."
			p.calculate    = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n (string-append (number->string (* n 100)) " %"))))
"""
			p.insert()

			p = Property()
			p.categories = [Category.byname('Misc')]
			p.name = "colonise"
			p.displayname = "Can Colonise Planets"
			p.desc = "Can the ship colonise planets/"
			p.calculate = """\
(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n 
			(if (> n 1) "Yes" "No"))))
"""
			p.insert()

			c = Component()
			c.categories = [Category.byname('Combat')]
			c.name = "Missile"
			c.desc = "Missile which does 1HP of damage."
			c.properties  = {}
			c.properties[Property.byname('primary-damage')] = None
			c.insert()

			c = Component()
			c.categories = [Category.byname('Combat')]
			c.name = "Laser"
			c.desc = "Lasers which do 1HP of damage."
			c.properties  = {}
			c.properties[Property.byname('backup-damage')] = """(lambda (design) 0.25)"""
			c.insert()

			c = Component()
			c.categories = [Category.byname('Combat')]
			c.name = "Armor Plate"
			c.desc = "Armor Plate which absorbes 1HP of damage."
			c.properties  = {}
			c.properties[Property.byname('hp')] = None
			c.insert()

			c = Component()
			c.categories = [Category.byname('Misc')]
			c.name = "Colonisation Pod"
			c.desc = "A part which allows a ship to colonise a planet."
			c.properties  = {}
			c.properties[Property.byname('colonise')] = None
			c.insert()

			c = Component()
			c.categories = [Category.byname('Misc')]
			c.name = "Escape Thrusters"
			c.desc = "A part which allows a ship to escape combat."
			c.properties  = {}
			c.properties[Property.byname('escape')] = """(lambda (design) 0.25)"""
			c.insert()

			c = Component()
			c.categories = [Category.byname('Misc')]
			c.name = "Primary Engine"
			c.desc = "A part which allows a ship to move through space."
			c.properties  = {}
			c.properties[Property.byname('speed')] = """(lambda (design) 1000000)"""
			c.insert()

			d = Design()
			d.name  = "Scout"
			d.desc  = "A fast light ship with advanced sensors."
			d.owner = -1
			d.categories = [Category.byname('Misc')]
			d.components = []
			d.components.append((Component.byname('Escape Thrusters'), 4))
			d.components.append((Component.byname('Armor Plate'),      2))
			d.components.append((Component.byname('Primary Engine'),   5))
			d.insert()
	
			d = Design()
			d.name  = "Frigate"
			d.desc  = "A general purpose ship with weapons and ability to colonise new planets."
			d.owner = -1
			d.categories = [Category.byname('Misc')]
			d.components = []
			d.components.append((Component.byname('Armor Plate'),      4))
			d.components.append((Component.byname('Primary Engine'),   2))
			d.components.append((Component.byname('Colonisation Pod'), 1))
			d.components.append((Component.byname('Missile'),          2))
			d.insert()

			d = Design()
			d.name  = "Battleship"
			d.desc  = "A heavy ship who's main purpose is to blow up other ships."
			d.owner = -1
			d.categories = [Category.byname('Misc')]
			d.components = []
			d.components.append((Component.byname('Armor Plate'),      6))
			d.components.append((Component.byname('Primary Engine'),   3))
			d.components.append((Component.byname('Missile'),          3))
			d.components.append((Component.byname('Laser'),            4))
			d.insert()

			trans.commit()
		except:
			trans.rollback()
			raise


		# FIXME: Need to populate the database with the MiniSec design stuff,
		#  - Firepower
		#  - Armor/HP
		#  - Speed
		#  - Sensors (scouts ability to disappear)....
		pass


	def populate(self, seed, system_min, system_max, planet_min, planet_max):
		"""\
		--populate <game> <random seed> <min systems> <max systems> <min planets> <max planets>
		
			Populate a universe with a number of systems and planets.
			The number of systems in the universe is dictated by min/max systems.
			The number of planets per system is dictated by min/max planets.
		"""
		dbconn.use(self.game)
		trans = dbconn.begin()
		try:
			MinisecRuleset.populate(self, seed, system_min, system_max, planet_min, planet_max)

			# Add a random smattering of resources to planets...
			r = random.Random()
			r.seed(int(seed))

			for planetid, time in Object.bytype('tp.server.rules.base.objects.Planet'):
				planet = Object(id=planetid)

				ids = r.sample(range(1, 4), r.randint(0, 3))
				for id in ids:
					planet.resources_add(id, r.randint(0, 10),   Planet.ACCESSABLE)
					planet.resources_add(id, r.randint(0, 100),  Planet.MINABLE)
					planet.resources_add(id, r.randint(0, 1000), Planet.INACCESSABLE)

				planet.save()


			trans.commit()
		except:
			trans.rollback()
			raise


	def player(self, username, password, email='Unknown', comment='A Minisec Player'):
		"""\
		Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
		"""
		dbconn.use(self.game)
	
		trans = dbconn.begin()
		try:
			user, system, planet, fleet = MinisecRuleset.player(self, username, password, email, comment)

			# Get the player's planet object and add the empire capital
			planet.resources_add(10, 1)
			planet.resources_add(11, 1)
			planet.save()

			trans.commit()
		except:
			trans.rollback()
			raise
