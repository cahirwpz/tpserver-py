#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.bases import SQLBase

from collections import MutableMapping

class ParameterDictMixin( MutableMapping ):#{{{
	_row_type = None

	__map	= property( lambda self: self.parameters )

	def __getitem__( self, key ):
		return self.__map[ key ].parameter

	def __setitem__( self, key, value ):
		item = self.__map.get( key, None )

		if item is None:
			self.__map[ key ] = self._row_type( name = key, parameter = value )
		else:
			item.parameter = value

	def __delitem__(self, key):
		del self.__map[ key ]

	def __contains__( self, key ):
		return key in self.__map

	def __iter__( self ):
		return self.__map.__iter__()

	def __len__( self ):
		return self.__map.__len__()
#}}}

class ParameterDesc( object ):#{{{
	def __init__( self, type, level, default = None, description = None ):
		self.type			= type
		self.level			= level
		self.default		= default
		self.description	= description
#}}}

class Parameter( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',    Integer, index = True, primary_key = True ),
				Column('type',  String(31), nullable = False ))

		cols = cls.__table__.c

		mapper( cls, cls.__table__, polymorphic_on = cols.type, polymorphic_identity = 'None' )
#}}}

__all__ = [ 'ParameterDictMixin', 'ParameterDesc', 'Parameter' ]
