#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.bases.SQL import SQLBase

class Reference( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',          Integer,     index = True, primary_key = True),
				Column('value',       Integer,     nullable = False),
				Column('description', Binary,      nullable = False),
				Column('reference',   String(255), nullable = False))

		mapper( cls, cls.__table__ )
#}}}

__all__ = [ 'Reference' ]
