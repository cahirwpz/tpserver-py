"""\
How to tell objects what to do.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.db import *
from tp import netlib
from SQL import SQLBase, SQLTypedBase, SQLTypedTable, quickimport, NoSuch
from tp.server.db import dbconn

from config import admin

class Order(SQLTypedBase):
	"""
	No description.
	"""

	table = Table('orders',
		Column('game', 	    Integer,     nullable=False, index=True),
		Column('id',	    Integer,     nullable=False, index=True, primary_key=True),
		Column('type',	    String(255), nullable=False, index=True),
		Column('oid',       Integer,     nullable=False, index=True),
		Column('slot',      Integer,     nullable=False, index=True),
		Column('worked',    Integer,     nullable=False),
		Column('time',	    DateTime,    nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		UniqueConstraint('oid', 'slot'),
		ForeignKeyConstraint(['oid'],  ['object.id']),
		ForeignKeyConstraint(['game'], ['game.id']),
	)
	Index('idx_order_oidslot', table.c.oid, table.c.slot)

	table_extra = SQLTypedTable('orders')

	def realid(cls, oid, slot):
		"""\
		Order.realid(objectid, slot) -> id
		
		Returns the database id for the order found on object at slot.
		"""
		t = cls.table
		result = select([t], (t.c.oid==oid) & (t.c.slot==slot)).execute().fetchall()
		if len(result) != 1:
			return -1
		else:
			return result[0]['id']
	realid = classmethod(realid)

	def number(cls, oid):
		"""\
		Order.number(objectid) -> number

		Returns the number of orders on an object.
		"""
		t = cls.table
		return select([func.count(t.c.id).label('count')], t.c.oid==oid).execute().fetchall()[0]['count']
	number = classmethod(number)

	def active(cls, type=None):
		"""\
		Order.active(type) -> ids

		Returns the ids of the given type which are in slot 0.
		"""
		t = cls.table
		if type is None:
			s = select([t.c.id], t.c.slot==0)
		else:
			s = select([t.c.id], (t.c.slot==0) & (t.c.type in type))
		return s.execute().fetchall()
	active = classmethod(active)

	def desc_packet(cls, sequence, typeno):
		"""\
		Order.desc_packet(sequence, typeno)

		Builds an order description packet for the specified order type.
		"""
		arguments = []
		for attribute in cls.attributes.values():
			if attribute.level != 'private':
				arguments.append((attribute.name, attribute.type, attribute.desc))

		# FIXME: This should send a correct last modified time
		return netlib.objects.OrderDesc(sequence, typeno, cls.__name__, cls.__doc__, arguments, 0)
	desc_packet = classmethod(desc_packet)

	def packet(cls, typeno):
		"""
		Return the class needed to create a packet for this type of order.
		"""
		# This is given a typeno because different rulesets may have different
		# typeno for the same Order type.
		return cls.desc_packet(0, typeno).build()
	packet = classmethod(packet)

	def __init__(self, oid=None, slot=None, type=None, id=None):
		if oid != None and slot != None:
			id = self.realid(oid, slot)
		else:
			id = None
		
		self.worked = 0
		SQLTypedBase.__init__(self, id, type)

	def allowed(self, user):
		# FIXME: This is a hack.
		return (user.id in admin) or (hasattr(self.object, "owner") and self.object.owner == user.id)

	def object(self):
		if not hasattr(self, "_object"):
			from Object import Object
			self._object = Object(self.oid)
		return self._object
	object = property(object)

	def insert(self):
		trans = dbconn.begin()
		try:
			t = self.table
		
			number = self.number(self.oid)
			if self.slot == -1:
				self.slot = number
			elif self.slot <= number:
				# Need to move all the other orders down
				t = self.table
				update(t, (t.c.slot>=self.slot) & (t.c.oid==self.oid)).execute(slot=(t.c.slot+1))
			else:
				raise NoSuch("Cannot insert to that slot number.")
			
			self.save()

			trans.commit()
		except Exception, e:
			trans.rollback()
			raise

	def save(self):
		trans = dbconn.begin()
		try:
			self.object.save()	
			if not hasattr(self, 'id'):
				id = self.realid(self.oid, self.slot)
				if id != -1:
					self.id = id
			SQLTypedBase.save(self)

			trans.commit()
		except Exception, e:
			trans.rollback()
			raise

	def remove(self):
		trans = dbconn.begin()
		try:
			# Move the other orders down
			t = self.table
			t.update((t.c.slot>=self.slot) & (t.c.oid==self.oid)).execute(slot=(t.c.slot-1))

			self.object.save()
			SQLTypedBase.remove(self)

			trans.commit()
		except Exception, e:
			trans.rollback()
			raise

	def to_packet(self, user, sequence):
		typeno = user.playing.ruleset.typeno(self)

		# Preset arguments
		args = [sequence, self.oid, self.slot, typeno, self.turns(), self.resources()]
		SQLTypedBase.to_packet(self, user, sequence, args)
		print self, args
		return self.packet(typeno)(*args)

	def from_packet(cls, user, packet):
		self = SQLTypedBase.from_packet(cls, user, packet)

		self.oid = packet.id
		del self.id

		return self
	from_packet = classmethod(from_packet)

	def __str__(self):
		if hasattr(self, 'id'):
			return "<Order type=%s id=%s oid=%s slot=%s>" % (self.type, self.id, self.oid, self.slot)
		else:
			return "<Order type=%s id=XX oid=%s slot=%s>" % (self.type, self.oid, self.slot)

	def turns(self, turns=0):
		"""\
		Number of turns this order will take to complete.
		"""
		return turns + 0
	
	def resources(self):
		"""\
		The resources this order will consume/use. (Negative for producing).
		"""
		return []
		
