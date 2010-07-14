#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

class ObjectParam( object ):#{{{
	__maps_to__ = 'object'

	@classmethod
	def InitMapper( cls, metadata, Parameter, Object ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('object_id', ForeignKey( Object.id ), nullable = True ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'Object', properties = {
			'object': relation( Object,
				uselist = False )
			})
#}}}

__all__ = [ 'ObjectParam' ]
