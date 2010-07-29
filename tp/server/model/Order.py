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

__all__ = [ 'Order' ]
