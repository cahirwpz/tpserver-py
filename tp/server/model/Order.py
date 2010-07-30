#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref
from sqlalchemy.orm.collections import attribute_mapped_collection

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
				Column('eta',    Integer,     nullable = False, default = 0),
				Column('mtime',  DateTime,    nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		mapper( cls, cls.__table__ )

#{{{
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

__all__ = [ 'Order', 'OrderParameter' ]
