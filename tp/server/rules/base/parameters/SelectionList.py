#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

from tp.server.model import ModelObject

class Selection( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',       Integer, index = True, primary_key = True ),
				Column('name',     String(255), nullable = False ),
				Column('number',   Integer, nullable = False, default = 0 ),
				Column('max',      Integer, nullable = False ))

		mapper( cls, cls.__table__ )

class SelectionList( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata, Selection ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',      Integer, index = True, primary_key = True ),
				Column('value_id', ForeignKey( Selection.id ), index = True, nullable = False ))

		mapper( cls, cls.__table__, properties = {
			'values' : relation( Selection,
				backref = 'list')
			})

class SelectionListParam( object ):
	@classmethod
	def InitMapper( cls, metadata, Parameter, ParameterType, SelectionList ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id', ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('list_id',  ForeignKey( SelectionList.id ), nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = ParameterType, properties = {
			'selections' : relation( SelectionList,
				collection_class = list )
			})

__all__ = [ 'Selection', 'SelectionList', 'SelectionListParam' ]
