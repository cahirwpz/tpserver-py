#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from SQL import SQLBase

class Order( SQLBase ):#{{{
	"""
	How to tell objects what to do.
	"""
	@classmethod
	def InitMapper( cls, metadata, Object ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',     Integer,     index = True, primary_key = True),
				Column('slot',   Integer,     nullable = False),
				Column('type',   String(255), nullable = False),
				Column('object', ForeignKey( Object.id )),
				Column('eta',    Integer,     nullable = False),
				Column('mtime',  DateTime,    nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		mapper( cls, cls.__table__ )

#{{{
	# types = {}

	# def __init__(self, oid = None, slot = None, type = None, id = None):
	#	if oid != None and slot != None:
	#		id = self.realid(oid, slot)
	#
	#	self.eta = 0

	# def insert(self):
	#	with DatabaseManager().session() as session:
	#		t = self.table
	#
	#		number = self.number(self.oid)
	#		if self.slot == -1:
	#			self.slot = number
	#		elif self.slot <= number:
	#			# Need to move all the other orders down
	#			update(t, (t.c.slot >= bindparam('s')) & (t.c.oid==bindparam('o')), {'slot': t.c.slot+1}).execute(s=self.slot, o=self.oid)
	#		else:
	#			raise NoSuchThing("Cannot insert to that slot number.")
	#
	#		self.save()

	# def save(self):
	#	with DatabaseManager().session() as session:
	#		# Update the modtime...
	#		self.object.save()
	#
	#		if not hasattr(self, 'id'):
	#			id = self.realid(self.oid, self.slot)
	#			if id != -1:
	#				self.id = id
	#
	#		SQLTypedBase.save(self)

	# def remove(self):
	#	with DatabaseManager().session() as session:
	#		# Move the other orders down
	#		t = self.table
	#		update(t, (t.c.slot >= bindparam('s')) & (t.c.oid==bindparam('o')), {'slot': t.c.slot-1}).execute(s=self.slot, o=self.oid)
	#
	#		self.object.save()
	#		SQLTypedBase.remove(self)

	# def realid(self, oid, slot):
	#	"""
	#	Order.realid(objectid, slot) -> id
	#	
	#	Returns the database id for the order found on object at slot.
	#	"""
	#	t = self.cls.table
	#	result = select([t.c.id], (t.c.oid==oid) & (t.c.slot==slot)).execute().fetchall()
	#	if len(result) != 1:
	#		return -1
	#	else:
	#		return result[0]['id']

	# def number(self, oid):
	#	"""
	#	Order.number(objectid) -> number
	#
	#	Returns the number of orders on an object.
	#	"""
	#	t = self.cls.table
	#	return select([func.count(t.c.id).label('count')], t.c.oid==oid).execute().fetchall()[0]['count']

	# def active(self, type=None):
	#	"""
	#	Order.active(type) -> ids
	#
	#	Returns the ids of the given type which are in slot 0.
	#	"""
	#	t = self.cls.table
	#	if type is None:
	#		s = select([t.c.id], t.c.slot==0)
	#	else:
	#		s = select([t.c.id], (t.c.slot==0) & (t.c.type in type))
	#	return [x[0] for x in s.execute().fetchall()]

	# def desc_packet(self, sequence, typeno):
	#	"""
	#	Order.desc_packet(sequence, typeno)
	#
	#	Builds an order description packet for the specified order type.
	#	"""
	#	arguments = []
	#	for attribute in cls.attributes.values():
	#		if attribute.level != 'private':
	#			arguments.append((attribute.name, attribute.type, attribute.desc))
	#
	#	# FIXME: This should send a correct last modified time
	#	return netlib.objects.OrderDesc(sequence, typeno, cls.__name__, cls.__doc__, arguments, 0)

	# def packet(self, typeno):
	#	"""
	#	Return the class needed to create a packet for this type of order.
	#	"""
	#	# This is given a typeno because different rulesets may have different
	#	# typeno for the same Order type.
	#	return self.cls.desc_packet(0, typeno).build()

	# def to_packet(self, user, sequence):
	#	self, args = SQLTypedBase.to_packet(self, user, sequence)
	#	
	#	typeno = user.playing.ruleset.typeno(self)
	#	print self.packet(typeno)
	#	return self.packet(typeno)(sequence, self.oid, self.slot, typeno, self.turns(), self.resources(), *args)

	# @classmethod
	# def from_packet(cls, user, packet):
	#	self = SQLTypedBase.from_packet(cls, user, packet)
	#
	#	self.oid = packet.id
	#	del self.id
	#
	#	return self

	# def turns( self, turns = 0 ):
	#	"""
	#	Number of turns this order will take to complete.
	#	"""
	#	return turns + 0
	
	# @property
	# def resources(self):
	#	"""
	#	The resources this order will consume/use. (Negative for producing).
	#	"""
	#	return []
#}}}

	def __str__(self):
		return "<Order type=%s id=%s oid=%s slot=%s>" % (self.type, self.id, self.oid, self.slot)
#}}}

__all__ = [ 'Order' ]
