#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

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

class NumberParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id', ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('value',    Integer, nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'Number' )
#}}}

__all__ = [ 'Number', 'NumberList', 'NumberParam' ]
