#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

class StringParam( object ):
	__maps_to__ = 'value'

	# TODO: constraint checking!
	#  - 'value' string must be shorter than 'max' characters
	@classmethod
	def InitMapper( cls, metadata, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id', ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('value',    Text, nullable = False ),
				Column('max',      Integer, nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'String' )

__all__ = [ 'StringParam' ]
