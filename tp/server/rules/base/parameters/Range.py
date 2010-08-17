#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

class RangeParam( object ):
	@classmethod
	def InitMapper( cls, metadata, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id', ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('value',    Integer, nullable = False ),
				Column('min',      Integer, nullable = False ),
				Column('max',      Integer, nullable = False ),
				Column('step',     Integer, nullable = False ),
				CheckConstraint( 'min < max' ),
				CheckConstraint( 'value >= min and value <= max' ),
				CheckConstraint( 'step < max - min' ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'Range' )

__all__ = [ 'RangeParam' ]
