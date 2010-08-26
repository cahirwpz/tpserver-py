#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.model import ModelObject, ByNameMixin

class NameMap( ModelObject, ByNameMixin ):
	"""
	Parameter type description class.
	"""

	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',   Integer,     index = True, primary_key = True),
				Column('name', String(255), index = True, nullable = False),
				UniqueConstraint('name'))

		mapper( cls, cls.__table__ )

	def __str__( self ):
		return '<%s@%s id="%s" name="%s">' % ( self.__origname__, self.__game__.name, self.id, self.name )

__all__ = [ 'NameMap' ]
