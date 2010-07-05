#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from SQL import SQLBase, SelectableByName

class Category( SQLBase, SelectableByName ):#{{{
	"""
	Categories which help group things together.
	"""

	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',          Integer, index = True, primary_key = True),
				Column('name',        String(255), index = True, nullable = False),
				Column('description', Text, nullable = False),
				Column('mtime',       DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()),
				UniqueConstraint( 'name' ) )

		mapper( cls, cls.__table__ )

	def __str__(self):
		return "<%s id=%s name=%s>" % ( self.__class__.__name__, self.id, self.name )
#}}}

__all__ = [ 'Category' ]
