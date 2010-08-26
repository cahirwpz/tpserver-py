#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref
from sqlalchemy.ext.orderinglist import ordering_list

from Model import ModelObject, ByNameMixin
from Parameter import AddedParameter

class Order( ModelObject ):
	"""
	How to tell objects what to do.
	"""
	@classmethod
	def InitMapper( cls, metadata, OrderType, Object, Player ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',        Integer,     index = True, primary_key = True),
				Column('slot',      Integer,     nullable = False),
				Column('type_id',   ForeignKey( OrderType.id ), nullable = False),
				Column('object_id', ForeignKey( Object.id ), nullable = True),
				Column('owner_id',  ForeignKey( Player.id ), index = True, nullable = True),
				Column('eta',       Integer,     nullable = False, default = 0),
				Column('mtime',     DateTime,    nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		cols = cls.__table__.c

		mapper( cls, cls.__table__, polymorphic_on = cols.type_id, properties = {
			'type': relation( OrderType,
				uselist = False ),
			'object': relation( Object,
				uselist = False,
				backref = backref( 'orders',
					collection_class = ordering_list('slot', count_from = 1),
					order_by = [ cols.slot ] )),
			'owner': relation( Player,
				uselist = False )
			})

	@classmethod
	def ByType( cls, type_name ):
		OrderType = cls.__game__.model.use( 'OrderType' )

		return OrderType.ByName( type_name ).orders

	def __str__( self ):
		return '<%s@%s id="%s" type="%s" object="%s">' % ( self.__origname__, self.__game__.name, self.id, self.type.name, self.object_id )

class OrderType( ModelObject, ByNameMixin ):
	"""
	Order type description class.
	"""

	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',   Integer,     index = True, primary_key = True),
				Column('name', String(255), index = True, nullable = False),
				UniqueConstraint('name'))

		mapper( cls, cls.__table__ )

	def __str__(self):
		return '<%s@%s id="%s" name="%s">' % ( self.__origname__, self.__game__.name, self.id, self.name )

class OrderParameter( AddedParameter ):
	def __str__( self ):
		return '<%s@%s order="%s" name="%s" param="%s">' % ( self.__origname__, self.__game__.name, self.order_id, self.name, self.param_id )

__all__ = [ 'Order', 'OrderType', 'OrderParameter' ]
