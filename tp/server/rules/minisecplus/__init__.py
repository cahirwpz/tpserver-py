
import random

from tp.server.db import dbconn

from tp.server.bases.Object   import Object
from tp.server.bases.Design   import Design
from tp.server.bases.Resource import Resource

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

	def initalise(self, seed=None):
		"""\
		Minisec 
		"""
		dbconn.use(self.game)

		trans = dbconn.begin()
		try:
			MinisecRuleset.initalise(self)

			# Add a bunch of "dummy" resources for "flair"
			r1 = Resource()
			r1.id           = 1
			r1.namesingular = 'Fruit Tree'
			r1.nameplural   = 'Fruit Trees'
			r1.unitsingular = ''
			r1.unitplural   = ''
			r1.desc         = 'Trees with lots of fruit on them!'
			r1.weight       = 10
			r1.size         = 30
			r1.insert()

			r2 = Resource()
			r2.id           = 2
			r2.namesingular = 'Weird Artifact'
			r2.nameplural   = 'Weird Artifacts'
			r2.unitsingular = ''
			r2.unitplural   = ''
			r2.desc         = 'Weird artifacts from a long time ago.'
			r2.weight       = 5
			r2.size         = 5
			r2.insert()

			r3 = Resource()
			r3.id           = 3
			r3.namesingular = 'Rock'
			r3.nameplural   = 'Rocks'
			r3.unitsingular = 'ton'
			r3.unitplural   = 'tons'
			r3.desc         = 'Rocks - Igneous, Sedimentary, Metamorphic, Oh my!'
			r3.weight       = 10
			r3.size         = 1
			r3.insert()

			r4 = Resource()
			r4.id           = 4
			r4.namesingular = 'Water'
			r4.nameplural   = 'Water'
			r4.unitsingular = 'kiloliter'
			r4.unitplural   = 'kiloliters'
			r4.desc         = 'That liquid stuff which carbon based life forms need.'
			r4.weight       = 1
			r4.size         = 1
			r4.insert()


			# These resources are actually useful
			# ==========================================================
			# Ship Parts
			# ----------------------------------------
			r = Resource()
			r.namesingular = 'Scout Part'
			r.nameplural   = 'Scout Parts'
			r.unitsingular = ''
			r.unitplural   = ''
			r.desc         = 'Parts which can be used to construct a scout ship.'
			r.weight       = 1
			r.size         = 1
			r.insert()

			r = Resource()
			r.namesingular = 'Frigate Part'
			r.nameplural   = 'Frigate Parts'
			r.unitsingular = ''
			r.unitplural   = ''
			r.desc         = 'Parts which can be used to construct a frigate ship.'
			r.weight       = 1
			r.size         = 1
			r.insert()

			r = Resource()
			r.namesingular = 'Battleship Part'
			r.nameplural   = 'Battleship Parts'
			r.unitsingular = ''
			r.unitplural   = ''
			r.desc         = 'Parts which can be used to construct a battleship ship.'
			r.weight       = 1
			r.size         = 1
			r.insert()

			# Homeworld indicator
			# ----------------------------------------
			r = Resource()
			r.id = 10
			r.namesingular = 'Empire Capital'
			r.nameplural   = ''
			r.unitsingular = ''
			r.unitplural   = ''
			r.desc         = 'The center of someone\'s intergalactic empire!'
			r.weight       = 0
			r.size         = 100000
			r.insert()

			# Planet Age indicator
			# ----------------------------------------
			r = Resource()
			r.id = 11
			r.namesingular = 'House'
			r.nameplural   = 'Housing'
			r.unitsingular = ''
			r.unitplural   = ''
			r.desc         = 'The basic place for people to live in.'
			r.weight       = 0
			r.size         = 100000
			r.insert()


			########################################################################

			d = Design()
			d.name  = "Scout"
			d.desc  = "A fast light ship with advanced sensors."
			d.owner = -1
			d.categories = []
			d.components = []
			d.insert()
	
			d = Design()
			d.name  = "Frigate"
			d.desc  = "A general purpose ship with weapons and ability to colonise new planets."
			d.owner = -1
			d.categories = []
			d.components = []
			d.insert()

			d = Design()
			d.name  = "Battleship"
			d.desc  = "A heavy ship who's main purpose is to blow up other ships."
			d.owner = -1
			d.categories = []
			d.components = []
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

			print "planets!!!", Object.bytype('tp.server.rules.base.objects.Planet')
			for planetid, time in Object.bytype('tp.server.rules.base.objects.Planet'):
				print "-->planet", planetid, time
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
