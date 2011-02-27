#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from tp.server.model import ModelObject

class ResourceQuantity( ModelObject ):	
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

class ResourceQuantityParam( object ):
	__maps_to__ = 'quantity'

	@classmethod
	def InitMapper( cls, metadata, Parameter, ParameterType, ResourceQuantity ):
		mapper( cls, inherits = Parameter, polymorphic_identity = ParameterType, properties = {
			'_quantity' : relation( ResourceQuantity,
				collection_class = attribute_mapped_collection('resource'))
			})

		cls.quantity = association_proxy('_quantity', 'quantity', creator = lambda k, v: ResourceQuantity( resource = k, **v ) )

	def remove( self, session ):
		for item in self._quantity:
			item.remove( session )

		super( ResourceQuantityParam, self ).remove( session )

__all__ = [ 'ResourceQuantity', 'ResourceQuantityParam' ]
