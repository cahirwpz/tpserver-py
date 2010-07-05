#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from tp.server.bases import SQLBase

class Resource( SQLBase ):	#{{{
	@classmethod
	def InitMapper( cls, metadata, Object, ResourceType ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('object_id',    ForeignKey( Object.id ), primary_key = True ),
				Column('type_id',      ForeignKey( ResourceType.id ), primary_key = True ),
				Column('accessible',   Integer, nullable = False, default = 0 ),
				Column('extractable',  Integer, nullable = False, default = 0 ),
				Column('inaccessible', Integer, nullable = False, default = 0 ))

		cols = cls.__table__.c

		Index('ix_%s_object_type' % cls.__tablename__, cols.object_id, cols.type_id)

		mapper( cls, cls.__table__, properties = {
			'object': relation( Object,
				uselist = False,
				backref = backref( 'resources' ),
				cascade = 'all'),
			'type': relation( ResourceType,
				uselist = False,
				cascade = 'all')
			})
#}}}

__all__ = [ 'Resource' ]
