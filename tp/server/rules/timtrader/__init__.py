#!/usr/bin/env python

import os.path

from tp.server.model import Model

from tp.server.rules.minisec import Ruleset
from tp.server.rules.base.orders import WaitOrder
from tp.server.rules.minisec.actions import TurnAction

import ProducersConsumers

class TimTraderRuleset( Ruleset ):
	"""
	TIM Trader Ruleset.

	TIM Trader is a simple game where the idea is to accumulate as much wealth as
	possible. You do this by moving goods around the universe.
	"""
	name = "timtrader"
	version = "0.0.1"

	files = os.path.join(os.path.dirname(__file__), "other")

	# The order orders and actions occur
	orderOfOrders = [
			WaitOrder, 			# Wait needs to occur last
			TurnAction,			# Increase the Universe's "Turn" value
	]

	def initModel( self ):
		Ruleset.initialise( self )

		ResourceType = self.game.objects.use( 'ResourceType' )

		# Create all the resources, they consist of,
		#  - One resource for each resource specified in resources.csv
		#  - One resource for each factory specified  in prodcon.csv

		ResourceType.FromCSV( os.path.join( self.files, "resources.csv" ) )

		resources = []

		for factory in ProducersConsumers.loadfile(os.path.join(self.files, "prodcon.csv")):
			# FIXME: Make these auto generated resources much nicer...
			# Ignore the special case factories which are also goods.

			r = ResourceType.ByName( factory.name )

			if r is None:
				r = ResourceType(
						name_singular	= factory.name,
						name_plural		= factory.name,
						description		= "",		
						weight			= 1000,
						size			= 1000 )
			else:
				r.description += "\n"

			r.description += "Converts"

			for product in factory.products:
				# FIXME: Should also display if usage of this resource is required to grow....
				r.description += "\n\t%s -> %s" % product

			r.products = factory.products

			resources.append( r )

		Model.add( *resources )

	def populate( self, seed, system_min, system_max, planet_min, planet_max ):
		"""
		--populate <game> <random seed> <min systems> <max systems> <min planets> <max planets>
		
			Populate a universe with a number of systems and planets.
			The number of systems in the universe is dictated by min/max systems.
			The number of planets per system is dictated by min/max planets.
		"""
		Ruleset.populate( self, seed, system_min, system_max, planet_min, planet_max )

		Object, ResourceType = self.game.objects.use( 'Object', 'ResourceType' )

		ship_parts_factory = ResourceType.ByName('Ship Parts Factory')

		Minerals	= [ ResourceType.ByName( name ) for name in [ 'Uranium', 'Iron Ore' ] ]
		Growing		= []
		Factories	= []

		for planet in Object.ByType('Planet'):
			# FIXME: Add minerals Iron, Uranium
			mine = False

			for mineral in Minerals:
				# Does this planet have this mineral
				if self.random.random() * 100 > mineral.probability:
					# Add a smattering of minerals 
					planet.resources[ mineral ] = { 'extractable' : self.random( 0, mineral.density ) }

					mine = True

			# Add a mine to each planet which has minerals
			if mine:
				planet.resources[ ResourceType.ByName('Mine') ] = { 'accessible' : 1 }
			
			# FIXME: Add growing resources
			for resource in Growing:
				if self.random.random() * 100 > resource.probability:
					# Add a smattering of breeding grounds
					planet.resources[ ResourceType.ByName('') ] = { 'accessible' : 1 }
					
					# Add a smattering of the same stocks
					planet.resources[ ResourceType.ByName('') ] = { 'extractable' : self.random.randint( 0, resource.density ) }

					# Add 1 fishery/slaughter house to each location

			# FIXME: Add a other industries in random locations
			for factory in Factories:
				pass

			# FIXME: Add a bunch of cities

	def addPlayer( self, username, password, email = 'Unknown', comment = 'A TimTrader Player' ):
		"""
		Create a Solar System, Planet, and initial Fleet for the player, positioned randomly within the Universe.
		"""
		user, system, planet, fleet = Ruleset.addPlayer( self, username, password, email, comment )

		ResourceType = self.game.objects.use( 'ResourceType' )

		# Get the player's planet object and add the empire capital
		planet.resources = {
				ResourceType.ByName('Header Quarter') : { 'accessible' : 1 },
				ResourceType.ByName('Credit')         : { 'accessible' : 10000 } }

		Model.add( planet )

__all__ = [ 'TimTraderRuleset' ]
