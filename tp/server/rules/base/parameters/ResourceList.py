#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from tp.server.bases import SQLBase, TableListMixin

class ResourceCount( SQLBase ):	#{{{
	@classmethod
	def InitMapper( cls, metadata, ResourceType ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',           Integer, index = True, primary_key = True ),
				Column('type_id',      ForeignKey( ResourceType.id ), index = True ),
				Column('accessible',   Integer, nullable = False, default = 0 ),
				Column('extractable',  Integer, nullable = False, default = 0 ),
				Column('inaccessible', Integer, nullable = False, default = 0 ))

		mapper( cls, cls.__table__, properties = {
			'type': relation( ResourceType,
				uselist = False )
			})
#}}}

class ResourceList( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, Item ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id', ForeignKey( Parameter.id ), primary_key = True ),
				Column('item_id',  ForeignKey( Item.id ), primary_key = True ))

		cols = cls.__table__.c

		Index('ix_%s_param_item' % cls.__tablename__, cols.param_id, cols.item_id)

		mapper( cls, cls.__table__, properties = {
			'parameter' : relation( Parameter,
				uselist = False,
				backref = backref( 'resources' ),
				cascade = 'all' ),
			'resource' : relation( Item,
				uselist = False,
				backref = backref( 'parameters' ),
				cascade = 'all' )
			})
#}}}

class ResourceListParam( TableListMixin ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, ResourceList ):
		mapper( cls, inherits = Parameter, polymorphic_identity = 'ResourceList' )

		cls._item_type = ResourceList
		cls._item_name = 'resource'
		cls._list_attr = 'resources'
#}}}

__all__ = [ 'ResourceCount', 'ResourceList', 'ResourceListParam' ]
