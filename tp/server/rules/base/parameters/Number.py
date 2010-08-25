#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

class NumberParam( object ):
	__maps_to__ = 'value'

	@classmethod
	def InitMapper( cls, metadata, Parameter, ParameterType ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id', ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('value',    Integer, nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = ParameterType )

__all__ = [ 'NumberParam' ]
