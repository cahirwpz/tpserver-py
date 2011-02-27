#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from tp.server.model import ModelObject

class DesignQuantity( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata, Parameter, Design ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), primary_key = True ),
				Column('design_id', ForeignKey( Design.id ), primary_key = True ),
				Column('quantity',  Integer ))

		cols = cls.__table__.c

		Index('ix_%s_param_design' % cls.__tablename__, cols.param_id, cols.design_id)

		mapper( cls, cls.__table__, properties = {
			'design': relation( Design,
				uselist = False )
			})

class DesignQuantityParam( object ):
	__maps_to__ = 'quantity'

	@classmethod
	def InitMapper( cls, metadata, Parameter, ParameterType, DesignQuantity ):
		mapper( cls, inherits = Parameter, polymorphic_identity = ParameterType, properties = {
			'_quantity' : relation( DesignQuantity,
				collection_class = attribute_mapped_collection('design'))
			})

		cls.quantity = association_proxy('_quantity', 'quantity', creator = lambda k, v: DesignQuantity( design = k, quantity = v ) )
	
	def remove( self, session ):
		for item in self._quantity:
			item.remove( session )

		super( DesignQuantityParam, self ).remove( session )

__all__ = [ 'DesignQuantity', 'DesignQuantityParam' ]
