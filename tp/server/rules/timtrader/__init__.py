
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
from tp.server.bases.Ruleset   import Ruleset as RulesetBase

class Ruleset(RulesetBase):
	"""
	TIM Trader Ruleset.

	TIM Trader is a simple game where the idea is to accumulate as much wealth as
	possible. You do this by moving goods around the universe.
	"""
	name = "TIM Trader"
	version = "0.0.1"

	files = os.path.join(os.path.dirname(__file__), "other")

	def initalise(self, seed=None):
		"""\
		TIM Trader
		"""

		dbconn.use(self.game)

		trans = dbconn.begin()
		try:
			RulesetBase.initalise(self)

			# Create all the resources, they consist of,
			#   - One resource for each resource specified in resources.csv
			#   - One resource for each factory specified  in prodcon.csv
			reader = csv.DictReader(open(os.path.join(self.files, "resources.csv"), "r"))
			for row in reader:
				r = Resource()
				for name, cell in row.iteritems():
					if cell is '':
						continue
					setattr(r, name, convert(getattr(Resource.table.c, name), cell))

				pprint.pprint(r.__dict__)

				r.insert()

			for factory in ProducersConsumers.loadfile():
				# Ignore the special case factories which are also goods.
				try:
					Resource.byname(factory.name)
					continue
				except NoSuch:
					pass

				r = Resource()
				r.namesingular = factory.name
				r.nameplural   = factory.name
				
				r.desc  = "Converts\n"
				for product in factory.products:
					# FIXME: Should also display if usage of this resource is required to grow....
					r.desc += "%s -> %s" % product

				r.weight = 1000
				r.size   = 1000


			reader = csv.DictReader(open(os.path.join(self.files, "categories.csv"), "r"))
			for row in reader:
				c = Category()
				for name, cell in row.iteritems():
					setattr(c, name, cell)

				pprint.pprint(c.__dict__)

				c.insert()

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
			RulesetBase.populate(self, seed, system_min, system_max, planet_min, planet_max)

			# Add a random smattering of resources to planets...
			r = random.Random()
			r.seed(int(seed))

			for planetid, time in Object.bytype('tp.server.rules.base.objects.Planet'):
				planet = Object(id=planetid)

				# FIXME: This needs to use the prop
				ids = r.sample(range(1, 4), r.randint(0, 3))
				for id in ids:
					planet.resources_add(id, r.randint(0, 10),   Planet.ACCESSABLE)
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
			user = RulesetBase.player(self, username, password, email, comment)

			# Get the player's planet object and add the empire capital
			planet.resources_add(Resource.byname('Homeworld') 1)
			planet.save()

			trans.commit()
		except:
			trans.rollback()
			raise
