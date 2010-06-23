#!/usr/bin/env python

from sqlalchemy import *

from tp.server.logging import msg
from tp.server.db import *

from SQL import SQLBase, SQLUtils
from Order import Order

class ObjectUtils( SQLUtils ):#{{{
	def bypos(self, pos, size=0, limit=-1, orderby=None):
		"""
		Object.bypos([x, y, z], size) -> [Object, ...]

		Return all objects which are centered inside a sphere centerd on
		size and radius of size.
		"""
		pos = long(pos[0]), long(pos[1]), long(pos[2])

		c = self.cls.table.c

		bp_x = bindparam('x')
		bp_y = bindparam('y')
		bp_z = bindparam('z')
		bp_s = bindparam('size')
		where = ((c.size+bp_s) >= \
					func.abs((c.posx-bp_x)) + \
					func.abs((c.posy-bp_y)) + \
					func.abs((c.posz-bp_z)))
#		where = (((c.size+bp_s)*(c.size+bp_s)) >= \
#					((c.posx-bp_x) * (c.posx-bp_x)) + \
#					((c.posy-bp_y) * (c.posy-bp_y)) + \
#					((c.posz-bp_z) * (c.posz-bp_z)))
		if orderby is None:
			orderby = [asc(c.time), desc(c.size)]

		s = select([c.id, c.time], where, order_by=orderby)
		if limit != -1:
			s.limit = limit

		results = s.execute(x=pos[0], y=pos[1], z=pos[2], size=size).fetchall()
		return [(x['id'], x['time']) for x in results]

	def byparent(self, id):
		"""
		byparent(id)

		Returns the objects which have a parent of this id.
		"""
		t = self.cls.table

		# FIXME: Need to figure out what is going on here..
		bp_id = bindparam('id')
		results = select([t.c.id, t.c.time], (t.c.parent==bp_id) & (t.c.id != bp_id)).execute(id=id).fetchall()
		return [(x['id'], x['time']) for x in results]

	def bytype(self, type):
		"""\
		bytype(id)

		Returns the objects which have a certain type.
		"""
		t = self.cls.table

		# FIXME: Need to figure out what is going on here..
		results = select([t.c.id, t.c.time], (t.c.type==bindparam('type'))).execute(type=type).fetchall()
		return [(x['id'], x['time']) for x in results]
#}}}

class Object( SQLBase ):#{{{
	"""
	The basis for all objects that exist.
	"""

	Utils = ObjectUtils()

	@classmethod
	def getTable( cls, name, metadata ):
		table = Table( name, metadata,
				Column('id',	    Integer,     index = True, primary_key = True),
				Column('parent_id', ForeignKey("%s.id" % name), nullable = True),
				Column('type',	    String(255), nullable = False),
				Column('name',      Binary,      nullable = False),
				Column('size',      Integer(64), nullable = False),
				Column('posx',      Integer(64), nullable = False, default = 0),
				Column('posy',      Integer(64), nullable = False, default = 0),
				Column('posz',      Integer(64), nullable = False, default = 0),
				Column('velx',      Integer(64), nullable = False, default = 0),
				Column('vely',      Integer(64), nullable = False, default = 0),
				Column('velz',      Integer(64), nullable = False, default = 0),
				Column('mtime',	    DateTime,    nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		Index('ix_%s_position' % name, table.c.posx, table.c.posy, table.c.posz)

		return table

	types = {}
	orderclasses = {}

	#bypos_size = [asc(table.c.size)]

	def __init__(self):
		self.name = "Unknown object"
		self.size = 0
		self.posx = 0
		self.posy = 0
		self.posz = 0
		self.velx = 0
		self.vely = 0
		self.velz = 0
		self.parent_id = None

	def protect(self, user):
		o = SQLBase.protect(self, user)
		if hasattr(self, "owner") and self.owner != user.id:
			msg( self.owner )
			o.orders = lambda: 0
			o.ordertypes = lambda: []
		return o

	def remove(self):
		# FIXME: Need to remove associated orders in a better way
		#delete(Order.table).execute(oid=self.id)
		# Remove any parenting on this object.
		t = Object.table
		update(t, t.c.parent==self.id, {t.c.parent: 0}).execute()
		SQLTypedBase.remove(self)
	
	@property
	def orders(self):
		"""
		orders()

		Returns the number of orders this object has.
		"""
		return Order.number(self.id)

	@property
	def ordertypes(self):
		"""
		ordertypes()

		Returns the valid order types for this object.
		"""
		# FIXME: This probably isn't good
		if not hasattr(self, "_ordertypes"):
			self._ordertypes = []
			for type in self.orderclasses:
				self._ordertypes.append(quickimport(type).typeno)
		
		return self._ordertypes

	@property
	def contains(self):
		"""
		contains()

		Returns the objects which this object contains.
		"""
		ids = self.Utils.byparent(self.id)
		if len(ids) > 0:
			return zip(*ids)[0]
		else:
			return tuple()

	@property
	def ghost(self):
		"""
		Returns true if this object should be removed.
		"""
		try:
			return self.owner == 0
		except AttributeError:
			return False

	def __str__(self):
		return "<Object %s id=%s>" % (".".join(self.type.split('.')[3:]), self.id)
#}}}

__all__ = [ 'Object' ]
