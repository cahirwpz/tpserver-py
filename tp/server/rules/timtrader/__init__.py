
import os.path
import csv
import random
import pprint

from tp.server.utils import ReparentOne
from tp.server.db import dbconn, convert

from tp.server.bases.SQL 	   import NoSuch
from tp.server.bases.Object    import Object
from tp.server.bases.Category  import Category
from tp.server.bases.Property  import Property
from tp.server.bases.Component import Component
from tp.server.bases.Design    import Design
from tp.server.bases.Ruleset   import Ruleset as RulesetBase

import tp.server.rules.base.orders.NOp as NOp
import tp.server.rules.base.actions.Move as MoveAction
import tp.server.rules.minisec.actions.Turn as Turn

from bases.Resource import Resource
	
SIZE = 10000000
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
			RulesetBase.initialise(self)

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

				r.transportable = bool(row['transportable'])

				r.insert()

			import ProducersConsumers
			for factory in ProducersConsumers.loadfile(os.path.join(self.files, "prodcon.csv")):
				# FIXME: Make these auto generated resources much nicer...
				# Ignore the special case factories which are also goods.
				try:
					r = Resource(Resource.byname(factory.name))
					r.desc += "\n"
				except NoSuch:
					r = Resource()
					r.namesingular = factory.name
					r.nameplural   = factory.name
					r.desc         = ""				
					r.weight = 1000
					r.size   = 1000

				r.desc  += "Converts"
				for product in factory.products:
					# FIXME: Should also display if usage of this resource is required to grow....
					r.desc += "\n\t%s -> %s" % product

				r.products = factory.products
				r.save()

			trans.commit()
		except:
			trans.rollback()
			raise

		# FIXME: Need to populate the database with the MiniSec design stuff,


	def populate(self, seed, system_min, system_max, planet_min, planet_max):
		"""\
		--populate <game> <random seed> <min systems> <max systems> <min planets> <max planets>
		
			Populate a universe with a number of systems and planets.
			The number of systems in the universe is dictated by min/max systems.
			The number of planets per system is dictated by min/max planets.
		"""
		# Convert arguments to integers
		seed, system_min, system_max, planet_min, planet_max = (int(seed), int(system_min), int(system_max), int(planet_min), int(planet_max))

		dbconn.use(self.game)
		trans = dbconn.begin()
		try:
			RulesetBase.populate(self, seed)

			r = Resource(Resource.byname('Ship Parts Factory'))

			# FIXME: Assuming that the Universe and the Galaxy exist.
			r = random.Random()
			r.seed(seed)

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
					mine = False
					for mineral in minerals:
						# Does this planet have this mineral
						if r.random()*100 > mineral.probability:
							# Add a smattering of minerals 
							planet.resources_add(id, r.randint(0, mineral.density), Planet.MINEABLE)
							mine = True

					# Add a mine to each planet which has minerals
					if mine:
						planet.resources_add(Resource.byname('Mine'), 1, Planet.ACCESSABLE)
						
					# FIXME: Add growing resources
					for grow in growing:
						if r.random()*100 > grow.probability:
							# Add a smattering of breeding grounds
							planet.resources_add(Resource.byname(''), 1, Planet.ACCESSABLE)
							
							# Add a smattering of the same stocks
							planet.resources_add(Resource.byname(''), r.randint(0, grow.density), Planet.MINEABLE)
						

							# Add 1 fishery/slaughter house to each location

					# FIXME: Add a other industries in random locations
					for factory in factories:
						pass

					# FIXME: Add a bunch of cities					
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

			# FIXME: Hack! This however means that player x will always end up in the same place..
			r = random.Random()
			r.seed(user.id)

			pos = r.randint(SIZE*-1, SIZE)*1000, r.randint(SIZE*-1, SIZE)*1000, r.randint(SIZE*-1, SIZE)*1000

			system = Object(type='tp.server.rules.base.objects.System')
			system.name = "%s Solar System" % username
			system.parent = 0
			system.size = r.randint(800000, 2000000)
			(system.posx, system.posy, junk) = pos
			ReparentOne(system)
			system.owner = user.id
			system.save()

			planet = Object(type='tp.server.rules.timtrader.objects.Planet')
			planet.name = "%s Planet" % username
			planet.parent = system.id
			planet.size = 100
			planet.posx = system.posx+r.randint(1,100)*1000
			planet.posy = system.posy+r.randint(1,100)*1000
			planet.owner = user.id

			# Get the player's planet object and add the empire capital
			planet.resources_add(Resource.byname('Header Quarter'), 1)
			planet.resources_add(Resource.byname('Credit'), 10000)

			planet.save()

			fleet = Object(type='tp.server.rules.minisec.objects.Fleet')
			fleet.parent = planet.id
			fleet.size = 3
			fleet.name = "%s First Fleet" % username
			fleet.ships = {1:3}
			(fleet.posx, fleet.posy, fleet.posz) = (planet.posx, planet.posy, planet.posz)
			fleet.owner = user.id
			fleet.save()

			trans.commit()
		except:
			trans.rollback()
			raise
