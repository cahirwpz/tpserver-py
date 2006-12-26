"""\
How to tell objects what to do.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp import netlib
from SQL import SQLBase, SQLTypedBase, SQLTypedTable, quickimport

from config import admin

class Order(SQLTypedBase):
	table = Table('order',
		Column('id',	    Integer,     nullable=False, default=0, index=True, primary_key=True),
		Column('type',	    String(255), nullable=False, index=True),
		Column('oid',       Integer,     nullable=True),
		Column('slot',      Integer,     nullable=False),
		Column('worked',    Integer,     nullable=False),
#		Column('time',	    DateTime,    nullable=False, index=True, onupdate=func.current_timestamp()),

		UniqueConstraint('oid', 'slot'),
		ForeignKeyConstraint(['oid'], ['object.id']),
	)
	Index('idx_order_oidslot', table.c.oid, table.c.slot)

	table_extra = SQLTypedTable('order')

	types = {}

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

	def desc_packet(cls, sequence, typeno):
		"""\
		Order.desc_packet(sequence, typeno)

		Builds an order description packet for the specified order type.
		"""
		# Pull out the arguments
		if not cls.types.has_key(typeno):
			raise NoSuch("No such order type.")

		order = cls(typeno=typeno)
		
		arguments = []
		for attribute in order.attributes.values():
			if attribute.level != 'private':
				arguments.append((attribute.name, attribute.type, attribute.desc))

		# FIXME: This should send a correct last modified time
		return netlib.objects.OrderDesc(sequence, typeno, order.__class__.__name__, order.__class__.__doc__, arguments, 0)
	desc_packet = classmethod(desc_packet)
	
	def load_all(cls):
		"""\
		Order.load_all()

		Loads all the possible order types from the database.
		"""
		for id in cls.types.keys():
			cls.desc_packet(0, id).register()
	load_all = classmethod(load_all)

	def __init__(self, oid=None, slot=None, packet=None, type=None, typeno=None, id=None):
		if oid != None and slot != None:
			id = self.realid(oid, slot)
		else:
			id = None
			
		SQLTypedBase.__init__(self, id, packet, type, typeno)

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
		try:
#			db.begin()

			t = self.table
		
			number = self.number(self.oid)
			if self.slot == -1:
				self.slot = number
			elif self.slot <= number:
				# Need to move all the other orders down
				t = self.table
				t.update((t.c.slot>=self.slot) & (t.c.oid==self.oid)).execute(slot=t.c.slot+1)
			else:
				raise NoSuch("Cannot insert to that slot number.")
			
			self.save()

		except Exception, e:
#			db.rollback()
			raise
		else:
#			db.commit()
			pass

	def save(self):
		try:
#			db.begin()
			
			self.object.save()	
			if not hasattr(self, 'id'):
				id = self.realid(self.oid, self.slot)
				if id != -1:
					self.id = id
			SQLTypedBase.save(self)
		except Exception, e:
#			db.rollback()
			raise
		else:
#			db.commit()
			pass

	def remove(self):
		try:
#			db.begin()
			
			# Move the other orders down
			t = self.table
			t.update((t.c.slot>=self.slot) & (t.c.oid==self.oid)).execute(slot=t.c.slot-1)

			self.object.save()
			SQLTypedBase.remove(self)

		except Exception, e:
#			db.rollback()
			raise
		else:
#			db.commit()
			pass

	def to_packet(self, sequence):
		# Preset arguments
		args = [sequence, self.oid, self.slot, self.typeno, self.turns(), self.resources()]
		SQLTypedBase.to_packet(self, sequence, args)
		print self, args
		return netlib.objects.Order(*args)

	def from_packet(self, packet):
		self.worked = 0

		self.oid = packet.id
		self.slot = packet.slot
		SQLTypedBase.from_packet(self, packet)

		del self.id

	def __str__(self):
		if hasattr(self, 'id'):
			return "<Order type=%s id=%s oid=%s slot=%s>" % (self.typeno, self.id, self.oid, self.slot)
		else:
			return "<Order type=%s id=XX oid=%s slot=%s>" % (self.typeno, self.oid, self.slot)

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
		
