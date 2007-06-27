
import os.path
import csv
import random
import pprint

from tp.server.db import dbconn, convert

from tp.server.bases.SQL 	   import NoSuch
from tp.server.bases.Object    import Object
from tp.server.bases.Resource  import Resource
from tp.server.bases.Category  import Category
from tp.server.bases.Property  import Property
from tp.server.bases.Component import Component
from tp.server.bases.Design    import Design
from tp.server.bases.Ruleset   import Ruleset as RulesetBase

import tp.server.rules.base.orders.NOp as NOp
import tp.server.rules.base.actions.Move as MoveAction
import tp.server.rules.minisec.actions.Turn as Turn

class Ruleset(RulesetBase):
	"""
	TIM Trader Ruleset.

	TIM Trader is a simple game where the idea is to accumulate as much wealth as
	possible. You do this by moving goods around the universe.
	"""
	name = "TIM Trader"
	version = "0.0.1"

	files = os.path.join(os.path.dirname(__file__), "other")
	# The order orders and actions occur
	orderOfOrders = [
			NOp, 				# NOp needs to occur last
			Turn, 				# Increase the Universe's "Turn" value
	]

	def initialise(self, seed=None):
		"""\
		TIM Trader
		"""
		dbconn.use(self.game)

		trans = dbconn.begin()
		try:
			# Create all the resources, they consist of,
			#   - One resource for each resource specified in resources.csv
			#   - One resource for each factory specified  in prodcon.csv
			reader = csv.DictReader(open(os.path.join(self.files, "resources.csv"), "r"))
			for row in reader:
				if row['namesingular'] is '':
					continue

				r = Resource()
				for name, cell in row.iteritems():
					if cell is '':
						continue
					try:
						setattr(r, name, convert(getattr(Resource.table.c, name), cell))
					except AttributeError, e:
						# FIXME: These shouldn't really occur...
						pass

				r.insert()

			import ProducersConsumers
			for factory in ProducersConsumers.loadfile(os.path.join(self.files, "prodcon.csv")):
				# FIXME: Make these auto generated resources much nicer...
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
					r.desc += "\t%s -> %s" % product

				r.weight = 1000
				r.size   = 1000

				r.insert()

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
			RulesetBase.populate(self, seed)

			# FIXME: Assuming that the Universe and the Galaxy exist.
			r = random.Random()
			r.seed(int(seed))

			# Create the actual systems and planets.
			for i in range(0, r.randint(system_min, system_max)):
				pos = r.randint(SIZE*-1, SIZE)*1000, r.randint(SIZE*-1, SIZE)*1000, r.randint(SIZE*-1, SIZE)*1000
				
				# Add system
				system = Object(type='tp.server.rules.base.objects.System')
				system.name = "System %s" % i
				system.size = r.randint(800000, 2000000)
				system.posx = pos[0]
				system.posy = pos[1]
				system.insert()
				ReparentOne(system)
				system.save()
				print "Created system (%s) with the id: %i" % (system.name, system.id)
				
				# In each system create a number of planets
				for j in range(0, r.randint(planet_min, planet_max)):
					planet = Object(type='tp.server.rules.timtrader.objects.Planet')
					planet.name = "Planet %i in %s" % (j, system.name)
					planet.size = r.randint(1000, 10000)
					planet.parent = system.id
					planet.posx = pos[0]+r.randint(1,100)*1000
					planet.posy = pos[1]+r.randint(1,100)*1000
					planet.insert()
					print "Created planet (%s) with the id: %i" % (planet.name, planet.id)

			# FIXME: Add minerals Iron, Uranium
			# Add a smattering of minerals 
			# Add a mine to each planet which has minerals

			# FIXME: Add growing resources
			# Add a smattering of breeding grounds
			# Add a smattering of the same stocks
			# Add 1 fishery/slaughter house to each location

			# FIXME: Add a other industries in random locations

			# FIXME: Add a bunch of cities


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
			planet.resources_add(Resource.byname('Header Quarter'), 1)
			planet.resources_add(Resource.byname('Credit'), 10000)
			planet.save()

			trans.commit()
		except:
			trans.rollback()
			raise
