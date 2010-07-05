#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.db import DatabaseManager

from SQL import SQLBase, SelectableByName

class ResourceType( SQLBase, SelectableByName ):#{{{
	"""
	ResourceTypes required to build stuff.
	"""

	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',	        Integer, index = True, primary_key = True),
				Column('name_singular', Text, nullable = False),
				Column('name_plural',   Text, nullable = False, default = ''),
				Column('unit_singular', Text, nullable = False, default = ''),
				Column('unit_plural',   Text, nullable = False, default = ''),
				Column('description',   Text, nullable = False),
				Column('weight',        Integer, nullable = False, default = 0),
				Column('size',          Integer, nullable = False, default = 0),
				Column('mtime',	        DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()),
				UniqueConstraint( 'name_singular', 'name_plural' ))

		mapper( cls, cls.__table__ )

	@classmethod
	def ByName( cls, name ):
		return DatabaseManager().query( cls ).filter_by( name_singular = name ).first()

	def __str__(self):
		return '<ResourceType "%s">' % self.name_singular
#}}}

__all__ = [ 'ResourceType' ]
