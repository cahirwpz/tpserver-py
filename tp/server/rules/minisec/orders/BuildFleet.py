#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.model import ParameterDesc, ParametrizedClass
from tp.server.rules.base.parameters import GenericReferenceListParam, StringParam

class BuildFleetOrder( object ):
	"""
	Build a new star ship fleet.
	"""
	__metaclass__ = ParametrizedClass

	ships = ParameterDesc(
		type		= GenericReferenceListParam,
		default		= None,
		level		= 'protected', 
		description	= "Ships to build and launch." )

	name = ParameterDesc(
		type		= StringParam,
		default		= dict( value = 'New Fleet' ),
		level		= 'protected',
		description	= "The new fleet's name." )

	@classmethod
	def InitMapper( cls, metadata, Order ):
		mapper( cls, inherits = Order, polymorphic_identity = 'BuildFleet' )

	@property
	def	typeno( self ):
		return 2

	def do(self):
		builder = Object(self.oid)

		if not hasattr(builder, "owner"):
			print "Could not do a build order because it was on an unownable object."
			self.remove()
		
		if self.turns() > 1:
			# Add another year to worked...
			self.worked += 1
			print "Worked %s, %s left until built." % (self.worked, self.turns())
			self.save()
			return
			
		# Build new fleet object
		fleet = Object(type='tp.server.rules.minisec.objects.Fleet')

		# Type Fleet
		fleet.parent = builder.id
		fleet.posx = builder.posx
		fleet.posy = builder.posy
		fleet.posz = builder.posz
		fleet.size = 1
		fleet.owner = builder.owner
		fleet.ships = self.ships
		fleet.insert()
		fleet.name = self.name
		fleet.save()

		message = Message()
		message.slot = -1
		message.bid = builder.owner
		message.subject = "Fleet built"
		
		message.body = """\
A new fleet (%s) has been built and is orbiting %s.
It consists of:
""" % (fleet.name, builder.name)

		for type, number in fleet.ships.items():
			if number > 1:
				message.body += "%s %ss" % (number, Fleet.ship_types[type])
			else:
				message.body += "%s %s" % (number, Fleet.ship_types[type])

		message.insert()

		self.remove()

	def turns(self, turns=0):
		time = {0:1, 1:2, 2:4}
	
		for type, number in self.ships.items():
			turns += time[type] * number

		return turns-self.worked

	def resources(self):
		return []

	def fn_ships(self, value=None):
		if value == None:
			returns = []
			for type, name in Fleet.ship_types.items():
				returns.append((type, name, -1))
			return returns, self.ships.items()
		else:
			ships = {}

			try:
				for type, number in value[1]:
					if not type in Fleet.ship_types.keys():
						raise ValueError("Invalid type selected")
					ships[type] = number
			except:
				pass

			self.ships = ships

	def fn_name(self, value=None):
		if value == None:
			return (255, self.name)
		else:
			self.name = value[1]

__all__ = [ 'BuildFleetOrder' ]
