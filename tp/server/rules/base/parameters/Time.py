#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

class TimeParam( object ):
	@classmethod
	def InitMapper( cls, metadata, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('turns',     Integer, nullable = False ),
				Column('max',       Integer, nullable = True ),
				CheckConstraint( 'turns >= 0 and turns <= max', name = 'turns in [0, max]' ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'Time' )

__all__ = [ 'TimeParam' ]
