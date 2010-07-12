#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.bases import Attribute
from tp.server.rules.base.parameters import PlayerParam, ResourceQuantityParam

class Planet( object ):#{{{
	__attributes__ = {
			'owner' : Attribute(
				type		= PlayerParam,
				level		= 'public',
				description	= "Current owner of the planet."),
			'resources' : Attribute(
				type		= ResourceQuantityParam,
				level		= 'protected',
				description	= "Resources present on the planet.") }

	@classmethod
	def InitMapper( cls, metadata, Object ):
		mapper( cls, inherits = Object, polymorphic_identity = 'Planet' )
	
	@property
	def owner( self ):
		try:
			return self['owner'].player
		except KeyError:
			PlayerParam = self.__game__.objects.use('PlayerParam')

			self['owner'] = PlayerParam( player = None ) # default

			return self['owner'].player

	@owner.setter
	def owner( self, value ):
		if value is not None:
			try:
				self['owner'].player = value
			except KeyError:
				PlayerParam = self.__game__.objects.use('PlayerParam')

				self['owner'] = PlayerParam( player = value )

	@property
	def resources( self ):
		try:
			self['resources']
		except KeyError:
			ResourceQuantityParam = self.__game__.objects.use('ResourceQuantityParam')

			self['resources'] = ResourceQuantityParam()

		return self['resources'].list

	@resources.setter
	def resources( self, value ):
		if value is not None:
			try:
				self['resources']
			except KeyError:
				ResourceQuantityParam = self.__game__.objects.use('ResourceQuantityParam')

				self['resources'] = ResourceQuantityParam()

			self['resources'].list = value

	@property
	def typeno( self ):
		return 3

#{{{
	#orderclasses = ('tp.server.rules.base.orders.NOp', 'tp.server.rules.minisec.orders.BuildFleet')

	#def ghost(self):
	#	"""
	#	Planets never die - even when owned by the universe.
	#	"""
	#	return False

	#damage = 0

	#def dead(self):
	#	"""
	#	Planets are dead when delt 12 damage.
	#	"""
	#	return self.damage > 12

	#def damage_do(self, damage):
	#	if type(damage) in (TupleType, ListType):
	#		for a in damage:
	#			self.damage_do(a)
	#	else:
	#		self.damage += damage

	#def damage_get(self, fail=False):
	#	return (6, 2)[fail]

	#def fn_resources(self, value=None):
	#	res = []
	#	for id, values in self.resources.items():
	#		res.append((id, values[0], values[1], values[2]))
	#
	#	return res

	#def resources_add(self, resource, amount, type=ACCESSABLE):
	#	if not self.resources.has_key(resource):
	#		self.resources[resource] = [0, 0, 0]
	#	self.resources[resource][type] += amount
	#
	#	if self.resources[resource][type] < 0:
	#		raise TypeError("Resources some how became negative!")
#}}}
#}}}

__all__ = [ 'Planet' ]
