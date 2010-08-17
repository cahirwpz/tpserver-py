#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, composite

from tp.server.model import Vector3D

class AbsCoordParam( object ):
	__maps_to__ = 'position'

	@classmethod
	def InitMapper( cls, metadata, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('x',         Integer, nullable = False ),
				Column('y',         Integer, nullable = False ),
				Column('z',         Integer, nullable = False ))

		cols = cls.__table__.c

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'AbsCoord',
				exclude_properties = [ 'param_id', 'x', 'y', 'z' ],
				properties = {
						'position': composite( Vector3D, cols.x, cols.y, cols.z ),
					})

__all__ = [ 'AbsCoordParam' ]
