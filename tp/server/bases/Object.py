"""\
The basis for all objects that exist.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.db import *
from tp import netlib
from config import admin
from SQL import SQLBase, SQLTypedBase, SQLTypedTable, quickimport
from Order import Order

class Object(SQLTypedBase):
	table = Table('object',
		Column('game',	    Integer,     nullable=False),
		Column('id',	    Integer,     nullable=False, index=True, primary_key=True),

		Column('type',	    String(255), nullable=False, index=True),
		Column('name',      Binary,      nullable=False),
		Column('size',      Integer,     nullable=False),
		Column('posx',      Integer,     nullable=False, default=0),
		Column('posy',      Integer,     nullable=False, default=0),
		Column('posz',      Integer,     nullable=False, default=0),
		Column('velx',      Integer,     nullable=False, default=0),
		Column('vely',      Integer,     nullable=False, default=0),
		Column('velz',      Integer,     nullable=False, default=0),
		Column('parent',    Integer,     nullable=True),
		Column('time',	    Integer,     nullable=False, index=True),

		ForeignKeyConstraint(['parent'], ['object.id']),
	)
	Index('idx_object_position', table.c.posx, table.c.posy, table.c.posz)

	table_extra = SQLTypedTable('object')

	types = {}
	orderclasses = {}

	def bypos(cls, pos, size=0, limit=-1, orderby="time, size DESC"):
		"""\
		Object.bypos([x, y, z], size) -> [Object, ...]

		Return all objects which are centered inside a sphere centerd on
		size and radius of size.
		"""
		pos = long(pos[0]), long(pos[1]), long(pos[2])

		c = cls.table.c
		where = (((c.size * c.size) + size**2) >= \
					(((c.posx-pos[0]) * (c.posx-pos[0])) + \
					 ((c.posy-pos[1]) * (c.posy-pos[1])) + \
					 ((c.posz-pos[2]) * (c.posz-pos[2]))))
		s = select([c.id, c.time], where)
		if limit != -1:
			s.limit = limit

		results = s.execute().fetchall()
		return [(x['id'], x['time']) for x in results]
	bypos = classmethod(bypos)

	def byparent(cls, id):
		"""\
		byparent(id)

		Returns the objects which have a parent of this id.
		"""
		t = cls.table
		results = select([t.c.id, t.c.time], t.c.parent==id).execute().fetchall()
		return [(x['id'], x['time']) for x in results]
	byparent = classmethod(byparent)

	def __init__(self, id=None, packet=None, type=None, typeno=None):
		self.name = "Unknown object"
		self.size = 0
		self.posx = 0
		self.posy = 0
		self.posz = 0
		self.velx = 0
		self.vely = 0
		self.velz = 0
		self.parent = 0

		SQLTypedBase.__init__(self, id, packet, type, typeno)

	def protect(self, user):
		o = SQLBase.protect(self, user)
		if not (user.id in admin) and (hasattr(self, "owner") and self.owner != user.id):
			def empty():
				return 0
			o.orders = empty
			
			def empty():
				return []
			o.ordertypes = empty
		return o

	def remove(self):
		# FIXME: Need to remove associated orders in a better way
		t = Order.table
		t.delete(oid==self.id)
		# Remove any parenting on this object.
		t = Object.table
		update(t, parent==self.id).execute(t.c.parent==0)
		SQLTypedBase.remove(self)
	
	def orders(self):
		"""\
		orders()

		Returns the number of orders this object has.
		"""
		return Order.number(self.id)

	def ordertypes(self):
		"""\
		ordertypes()

		Returns the valid order types for this object.
		"""
		if not hasattr(self, "_ordertypes"):
			self._ordertypes = []
			for type in self.orderclasses:
				self._ordertypes.append(quickimport(type).typeno)
		
		return self._ordertypes

	def contains(self):
		"""
		contains()

		Returns the objects which this object contains.
		"""
		ids = self.byparent(self.id)
		if len(ids) > 0:
			return zip(*ids)[0]
		else:
			return tuple()

	def to_packet(self, sequence):
		# Preset arguments
		args = [sequence, self.id, self.typeno, self.name, self.size, self.posx, self.posy, self.posz, self.velx, self.vely, self.velz, self.contains(), self.ordertypes(), self.orders(), self.time]
		SQLTypedBase.to_packet(self, sequence, args)
		print self, args
		return netlib.objects.Object(*args)

	def id_packet(cls):
		return netlib.objects.Object_IDSequence
	id_packet = classmethod(id_packet)

	def __str__(self):
		return "<Object %s id=%s>" % (".".join(self.type.split('.')[3:]), self.id)

	def ghost(self):
		"""\
		Returns true if this object should be removed.
		"""
		if hasattr(self, "owner"):
			return self.owner == 0
		else:
			return False
