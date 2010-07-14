#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

from tp.server.bases import SQLBase

class DesignQuantity( SQLBase ):#{{{
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
#}}}

class DesignQuantityParam( object ):#{{{
	__maps_to__ = 'list'

	@classmethod
	def InitMapper( cls, metadata, Parameter, DesignQuantity ):
		mapper( cls, inherits = Parameter, polymorphic_identity = 'DesignQuantityList', properties = {
			'list' : relation( DesignQuantity,
				cascade = 'all' )
			})
#}}}

__all__ = [ 'DesignQuantity', 'DesignQuantityParam' ]
