#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref, composite

from tp.server.db import DatabaseManager

from SQL import SQLBase
from Attributes import AttributeDictMixin

class Vector3D( object ):#{{{
	def __init__( self, x = 0, y = 0, z = 0 ):
		self.x = x
		self.y = y
		self.z = z

	def __composite_values__( self ):
		return [ self.x, self.y, self.z ]

	def __set_composite_values__( self, x, y, z ):
		self.x = x
		self.y = y
		self.z = z

	def __eq__( self, other ):
		return other.x == self.x and other.y == self.y and other.z == self.z

	def __ne__( self, other ):
		return not self.__eq__( other )
#}}}

class Object( SQLBase, AttributeDictMixin ):#{{{
	"""
	The basis for all objects that exist.
	"""

	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',	    Integer,     index = True, primary_key = True),
				Column('parent_id', ForeignKey( "%s.id" % cls.__tablename__ ), nullable = True),
				Column('type',	    String(255), nullable = False),
				Column('name',      Text,        nullable = False),
				Column('size',      Integer(64), nullable = False),
				Column('pos_x',     Integer(64), nullable = False, default = 0),
				Column('pos_y',     Integer(64), nullable = False, default = 0),
				Column('pos_z',     Integer(64), nullable = False, default = 0),
				Column('vel_x',     Integer(64), nullable = False, default = 0),
				Column('vel_y',     Integer(64), nullable = False, default = 0),
				Column('vel_z',     Integer(64), nullable = False, default = 0),
				Column('mtime',	    DateTime,    nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		cols = cls.__table__.c

		Index('ix_%s_position' % cls.__tablename__, cols.pos_x, cols.pos_y, cols.pos_z)

		mapper( cls, cls.__table__, polymorphic_on = cols.type, polymorphic_identity = 'Object', properties = {
			# Tree like hierarchy for objects ie. Universe => Solar systems => Planets => etc.
			'children': relation( cls,
				backref = backref( 'parent', remote_side = [ cols.id ] ),
				cascade = "all"),
			# Object position in 3D space
			'position': composite( Vector3D, cols.pos_x, cols.pos_y, cols.pos_z ),
			# Object velocity in 3D space
			'velocity': composite( Vector3D, cols.vel_x, cols.vel_y, cols.vel_z )
			})

	@classmethod
	def ByType( cls, type_id ):
		"""
		ByType( type_id )
	
		Returns the objects which have a certain type.
		"""
		return DatabaseManager().query( cls ).filter_by( type = type_id ).all()

#{{{
	# @classmethod
	# def ByPos( cls, center, size = 0, limit = -1, order_by = None ):
	#	"""
	#	Object.ByPos([x, y, z], size) -> [Object, ...]
	#
	#	Return all objects which are centered inside a sphere centerd on
	#	size and radius of size.
	#	"""
	#	pos = long(center[0]), long(center[1]), long(center[2])
	#
	#	c = cls.table.c
	#
	#	bp_x = bindparam('x')
	#	bp_y = bindparam('y')
	#	bp_z = bindparam('z')
	#	bp_s = bindparam('size')
	#	where = ((c.size + bp_s) >= \
	#			func.abs((c.pos_x - bp_x)) + \
	#			func.abs((c.pos_y - bp_y)) + \
	#			func.abs((c.pos_z - bp_z)))
	#	# where = (((c.size+bp_s)*(c.size+bp_s)) >= \
	#			# ((c.posx-bp_x) * (c.posx-bp_x)) + \
	#			# ((c.posy-bp_y) * (c.posy-bp_y)) + \
	#			# ((c.posz-bp_z) * (c.posz-bp_z)))
	#
	#	if order_by is None:
	#		order_by = [asc(c.mtime), desc(c.size)]
	#
	#	s = select([c.id, c.mtime], where, order_by = order_by)
	#
	#	if limit != -1:
	#		s.limit = limit
	#
	#	results = s.execute(x=pos[0], y=pos[1], z=pos[2], size=size).fetchall()
	#	return [(x['id'], x['time']) for x in results]
	
	# orderclasses = {}

	# bypos_size = [asc(table.c.size)]

	# def protect(self, user):
	#	o = SQLBase.protect(self, user)
	#	if hasattr(self, "owner") and self.owner != user.id:
	#		msg( self.owner )
	#		o.orders = lambda: 0
	#		o.ordertypes = lambda: []
	#	return o

	#@property
	#def orders(self):
	#	"""
	#	orders()
	#
	#	Returns the number of orders this object has.
	#	"""
	#	return Order.number(self.id)

	#@property
	#def ordertypes(self):
	#	"""
	#	ordertypes()
	#
	#	Returns the valid order types for this object.
	#	"""
	#	# FIXME: This probably isn't good
	#	if not hasattr(self, "_ordertypes"):
	#		self._ordertypes = []
	#		for type in self.orderclasses:
	#			self._ordertypes.append(quickimport(type).typeno)
	#	
	#	return self._ordertypes

	#@property
	#def ghost(self):
	#	"""
	#	Returns true if this object should be removed.
	#	"""
	#	try:
	#		return self.owner == 0
	#	except AttributeError:
	#		return False
#}}}

	def __str__(self):
		return '<%s@%s id="%s" type="%s">' % ( self.__origname__, self.__game__.name, self.id, self.type )
#}}}

__all__ = [ 'Object', 'Vector3D' ]
