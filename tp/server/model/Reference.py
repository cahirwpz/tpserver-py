#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

from Model import ModelObject, ByNameMixin

class Reference( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata, ReferenceType ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',      Integer, index = True, primary_key = True),
				Column('type_id', ForeignKey( ReferenceType.id ), nullable = False))

		cols = cls.__table__.c

		mapper( cls, cls.__table__, polymorphic_on = cols.type_id, properties = {
			'type': relation( ReferenceType,
				uselist = False )
			})
	
	def __str__( self ):
		return '<%s@%s id="%s" type="%s">' % ( self.__origname__, self.__game__.name, self.id, self.type.name )

class ReferenceType( ModelObject, ByNameMixin ):
	"""
	Reference type description class.
	"""

	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',   Integer,     index = True, primary_key = True),
				Column('name', String(255), index = True, nullable = False),
				UniqueConstraint('name'))

		mapper( cls, cls.__table__ )

	def __str__(self):
		return '<%s@%s id="%s" name="%s">' % ( self.__origname__, self.__game__.name, self.id, self.name )

__all__ = [ 'Reference', 'ReferenceType' ]
