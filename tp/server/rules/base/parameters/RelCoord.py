#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, composite

from tp.server.model import Vector3D

class RelCoordParam( object ):
	@classmethod
	def InitMapper( cls, metadata, Parameter, Object ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('x',         Integer, nullable = False ),
				Column('y',         Integer, nullable = False ),
				Column('z',         Integer, nullable = False ),
				Column('parent_id', ForeignKey( Object.id ), nullable = True ))

		cols = cls.__table__.c

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'RelCoord', properties = {
			'parent' : relation( Object,
				uselist = False ),
			# Object position in 3D space
			'vector': composite( Vector3D, cols.x, cols.y, cols.z ),
			})

__all__ = [ 'RelCoordParam' ]
