#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from tp.server.bases import SQLBase

class Number( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',     Integer, index = True, primary_key = True ),
				Column('number', Integer, nullable = False ))

		mapper( cls, cls.__table__ )
#}}}

class NumberList( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Number ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',      Integer, index = True, primary_key = True ),
				Column('item_id', ForeignKey( Number.id ), index = True, nullable = False ))

		mapper( cls, cls.__table__, properties = {
			'values' : relation( Number,
				backref = 'list',
				cascade = 'all' )
			})
#}}}

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

class Parameter( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',    Integer, index = True, primary_key = True ),
				Column('type',  String(15), nullable = False ))

		mapper( cls, cls.__table__ )
#}}}

__all__ = [ 'Selection', 'Number', 'SelectionList', 'NumberList', 'Parameter' ]
