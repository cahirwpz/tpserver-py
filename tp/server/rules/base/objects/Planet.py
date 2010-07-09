#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

class Planet( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Object, Player ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('object_id', ForeignKey( Object.id ), index = True, primary_key = True ),
				Column('owner_id',  ForeignKey( Player.id ), nullable = True ))

		mapper( cls, cls.__table__, inherits = Object, polymorphic_identity = 'Planet', properties = {
			'owner' : relation( Player,
				uselist = False,
				backref = backref( 'planets' ),
				cascade = 'all')
			})

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
