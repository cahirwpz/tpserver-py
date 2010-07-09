#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

class RelCoordParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, Object ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('x',         Integer, nullable = False ),
				Column('y',         Integer, nullable = False ),
				Column('z',         Integer, nullable = False ),
				Column('parent_id', ForeignKey( Object.id ), nullable = True ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'RelCoord', properties = {
			'parent' : relation( Object,
				uselist = False )
			})
#}}}

__all__ = [ 'RelCoordParam' ]
