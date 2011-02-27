#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

from Model import ModelObject
from Generic import NameMap

class Reference( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata, ReferenceType ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',      Integer, index = True, primary_key = True),
				Column('type_id', Integer, ForeignKey( ReferenceType.id ), nullable = False))

		cols = cls.__table__.c

		mapper( cls, cls.__table__, polymorphic_on = cols.type_id, properties = {
			'type': relation( ReferenceType,
				uselist = False )
			})
	
	def __str__( self ):
		return '<%s@%s id="%s" type="%s">' % ( self.__origname__, self.__game__.name, self.id, self.type.name )

class ReferenceType( NameMap ):
	"""
	Reference type description class.
	"""

__all__ = [ 'Reference', 'ReferenceType' ]
