#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from tp.server.bases import SQLBase

class Parameter( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',    Integer, index = True, primary_key = True ),
				Column('type',  String(31), nullable = False ))

		cols = cls.__table__.c

		mapper( cls, cls.__table__, polymorphic_on = cols.type, polymorphic_identity = 'None' )
#}}}

__all__ = [ 'Parameter' ]
