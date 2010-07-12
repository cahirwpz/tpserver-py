#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

from tp.server.bases import SQLBase

class ResourceQuantity( SQLBase ):	#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, ResourceType ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('parameter_id', ForeignKey( Parameter.id ), primary_key = True ),
				Column('resource_id',  ForeignKey( ResourceType.id ), primary_key = True ),
				Column('accessible',   Integer, nullable = False, default = 0 ),
				Column('extractable',  Integer, nullable = False, default = 0 ),
				Column('inaccessible', Integer, nullable = False, default = 0 ))

		cols = cls.__table__.c

		Index('ix_%s_parameter_resource' % cls.__tablename__, cols.parameter_id, cols.resource_id)

		mapper( cls, cls.__table__, properties = {
			'resource': relation( ResourceType,
				uselist = False )
			})
#}}}

class ResourceQuantityParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, ResourceQuantity ):
		mapper( cls, inherits = Parameter, polymorphic_identity = 'ResourceQuantityList', properties = {
			'list' : relation( ResourceQuantity,
				cascade = 'all' )
			})
#}}}

__all__ = [ 'ResourceQuantity', 'ResourceQuantityParam' ]
