#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.model import ParameterDesc, ParametrizedClass
from tp.server.rules.base.parameters import ObjectRefParam

class MergeFleetOrder( object ):
	"""
	Merge two fleets together.
	"""
	__metaclass__ = ParametrizedClass

	fleet = ParameterDesc(
			type		= ObjectRefParam,
			default		= None,
			level		= 'protected',
			description	= "Fleet to merge with.")

	@classmethod
	def InitMapper( cls, metadata, Order ):
		mapper( cls, inherits = Order, polymorphic_identity = 'MergeFleet' )

	@property
	def typeno( self ):
		return 4
	
	def do(self):
		# We need the original fleet
		fleet1 = Object(self.oid)
		
		# We need the other fleet
		if self.fleet != -1:
			fleet2 = Object(self.fleet)

		message = Message()
		message.slot = -1
		message.bid = fleet1.owner
		message.subject = "Merge Fleet failed."
		
		# Check the other object is actually a fleet...
		if self.fleet == -1 or fleet2.type.endswith('Fleet'):
			# Send message about the owner not matching...
			message.body = """\
The merge failed (of %s) because the merge target wasn't a fleet!
The merge order has been removed.
""" % (fleet1.name)
			message.insert()
			
			self.remove()
			return

		# Check they have the same owner :)
		if fleet1.owner != fleet2.owner:
			# Send message about the owner not matching...
			message.body = """\
The merge between %s and %s failed because you didn't own both fleets.
The merge order has been removed.
""" % (fleet1.name, fleet2.name)
			message.insert()
			
			self.remove()
			return
		
		# Check they are at the same position
		if (fleet1.posx, fleet1.posy, fleet1.posz) != (fleet2.posx, fleet2.posy, fleet2.posz):
			return

		# Merge the fleets
		for type, number in fleet1.ships.items():
			if fleet2.ships.has_key(type):
				fleet2.ships[type] += number
			else:
				fleet2.ships[type] = number
				
			del fleet1.ships[type]

		fleet1.save()
		# Remove the other fleet
		fleet2.remove()

		self.remove()

	def turns(self, turns=0):
		return turns+1

	def resources(self):
		return []

	def fn_fleet(self, value=None):
		if value == None:
			return self.fleet
		else:
			try:
				fleet = Object(value)
				if fleet.type != 'sobjects.Fleet':
					self.fleet = -1
				else:
					self.fleet = value
			except NoSuchThing:
				self.fleet = -1

			return

__all__ = [ 'MergeFleetOrder' ]
