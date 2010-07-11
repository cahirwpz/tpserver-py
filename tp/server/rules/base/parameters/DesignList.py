#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from tp.server.bases import SQLBase, TableListMixin

class DesignCount( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Design ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',        Integer, index = True, primary_key = True ),
				Column('design_id', ForeignKey( Design.id ), nullable = False ),
				Column('count',     Integer ))

		mapper( cls, cls.__table__, properties = {
			'design': relation( Design,
				uselist = False )
			})
#}}}

class DesignList( SQLBase ):#{{{
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
				backref = backref( 'designs' ),
				cascade = 'all' ),
			'design' : relation( Item,
				uselist = False,
				backref = backref( 'parameters' ),
				cascade = 'all' )
			})
#}}}

class DesignListParam( TableListMixin ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, DesignList ):
		mapper( cls, inherits = Parameter, polymorphic_identity = 'DesignList' )

		cls._item_type = DesignList
		cls._item_name = 'design'
		cls._list_attr = 'designs'
#}}}

__all__ = [ 'DesignCount', 'DesignList', 'DesignListParam' ]
