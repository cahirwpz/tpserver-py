#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from tp.server.bases import SQLBase

class Parameter( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',    Integer, index = True, primary_key = True ),
				Column('type',  String(15), nullable = False ))

		mapper( cls, cls.__table__ )
#}}}

__all__ = [ 'Parameter' ]
