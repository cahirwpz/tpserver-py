#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

from tp.server.model import SQLBase

class Selection( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',       Integer, index = True, primary_key = True ),
				Column('name',     String(255), nullable = False ),
				Column('number',   Integer, nullable = False, default = 0 ),
				Column('max',      Integer, nullable = False ))

		mapper( cls, cls.__table__ )
#}}}

class SelectionList( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Selection ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',      Integer, index = True, primary_key = True ),
				Column('value_id', ForeignKey( Selection.id ), index = True, nullable = False ))

		mapper( cls, cls.__table__, properties = {
			'values' : relation( Selection,
				backref = 'list',
				cascade = 'all' )
			})
#}}}

class SelectionListParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, SelectionList ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id', ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('list_id',  ForeignKey( SelectionList.id ), nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'SelectionList', properties = {
			'selections' : relation( SelectionList,
				cascade = 'all',
				collection_class = list )
			})
#}}}

__all__ = [ 'Selection', 'SelectionList', 'SelectionListParam' ]
