#!/usr/bin/env python

from tp.server.model import ParameterDesc, ParametrizedClass
from tp.server.rules.base.parameters import PlayerParam, ResourceQuantityParam

class Planet( object ):
	__metaclass__ = ParametrizedClass

	owner = ParameterDesc(
		type		= PlayerParam,
		level		= 'public',
		description	= "Current owner of the planet.")

	resources = ParameterDesc(
		type		= ResourceQuantityParam,
		level		= 'protected',
		description	= "Resources present on the planet.")


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

__all__ = [ 'Planet' ]
