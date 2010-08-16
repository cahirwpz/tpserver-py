#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from Model import ModelObject

class Reference( ModelObject ):#{{{
	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',          Integer,     index = True, primary_key = True),
				Column('value',       Integer,     nullable = False),
				Column('description', Binary,      nullable = False),
				Column('reference',   String(255), nullable = False))

		mapper( cls, cls.__table__ )
	
	def __str__( self ):
		return '<%s@%s id="%d">' % ( self.__origname__, self.__game__.__name__, self.id )
#}}}

__all__ = [ 'Reference' ]
