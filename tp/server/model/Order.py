#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref
from sqlalchemy.orm.collections import attribute_mapped_collection

from SQL import SQLBase, SelectableByName

class Order( SQLBase ):#{{{
	"""
	How to tell objects what to do.
	"""
	@classmethod
	def InitMapper( cls, metadata, OrderType, Object ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',        Integer,     index = True, primary_key = True),
				Column('slot',      Integer,     nullable = False),
				Column('type_id',   ForeignKey( OrderType.id ), nullable = False),
				Column('object_id', ForeignKey( Object.id ), nullable = True),
				Column('eta',       Integer,     nullable = False, default = 0),
				Column('mtime',     DateTime,    nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		cols = cls.__table__.c

		mapper( cls, cls.__table__, polymorphic_on = cols.type_id, properties = {
			'type': relation( OrderType,
				uselist = False ),
			'object': relation( Object,
				uselist = False,
				backref = backref( 'orders' ))
			})

	@classmethod
	def ByType( cls, type_name ):
		OrderType = cls.__game__.model.use( 'OrderType' )

		return OrderType.ByName( type_name ).orders

	def __str__( self ):
		return '<%s@%s id="%s" type="%s" object="%s">' % ( self.__origname__, self.__game__.name, self.id, self.type.name, self.object_id )
#}}}

class OrderType( SQLBase, SelectableByName ):#{{{
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
#}}}

class OrderParameter( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Order, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('order_id', ForeignKey( Order.id ), index = True, primary_key = True ),
				Column('name',     String( 255 ), index = True, primary_key = True ),
				Column('param_id', ForeignKey( Parameter.id ), nullable = True ))

		mapper( cls, cls.__table__, properties = {
			'order' : relation( Order,
				uselist = False,
				backref = backref( 'parameters',
					collection_class = attribute_mapped_collection( 'name' ))
				),
			'parameter' : relation( Parameter,
				uselist = False )
			})
	
	def remove( self, session ):
		self.parameter.remove( session )

		session.delete( self )
	#}}}

__all__ = [ 'Order', 'OrderType', 'OrderParameter' ]
