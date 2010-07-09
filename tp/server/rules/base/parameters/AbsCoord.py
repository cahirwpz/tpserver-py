#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

class AbsCoordParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('x',         Integer, nullable = False ),
				Column('y',         Integer, nullable = False ),
				Column('z',         Integer, nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'AbsCoord' )
#}}}

__all__ = [ 'AbsCoordParam' ]
