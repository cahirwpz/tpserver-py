#!/usr/bin/env python

import inspect

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

from tp.server.model import ModelObject, ByNameMixin

class ParameterDesc( object ):
	def __init__( self, type, level, default = None, description = None ):
		self.type			= type
		self.level			= level
		self.default		= default
		self.description	= description

	def __check( self, obj ):
		try:
			parameter = obj.parameters[ self.name ]
		except KeyError:
			ObjectParameter, Parameter = obj.__game__.model.use( 'ObjectParameter', self.type.__name__ )

			obj.parameters[ self.name ] = ObjectParameter( name = self.name, parameter = Parameter() )

			parameter = obj.parameters[ self.name ]

		return parameter

	def __get__( self, obj, objtype ):
		if obj is None:
			return self

		parameter = self.__check( obj )

		if hasattr( self.type, '__maps_to__' ):
			# debug( "getting value of %s.%s", self.name, self.type.__maps_to__ )
			return getattr( parameter.parameter, self.type.__maps_to__ )
		else:
			# debug( "getting value of %s", self.name )
			return parameter.parameter

	def __set__( self, obj, value ):
		if value is not None:
			parameter = self.__check( obj )

			if hasattr( self.type, '__maps_to__' ):
				# debug( "setting %s.%s to %s", self.name, self.type.__maps_to__, value )
				setattr( parameter.parameter, self.type.__maps_to__, value )
			else:
				# debug( "setting %s to %s", self.name, value )
				parameter.parameter = value
	
	def __str__( self ):
		if not self.__name__:
			return "<%s object at 0x%x>" % ( self.__class__.__name__, id(self) )
		else:
			return "<%s \'%s\' object at 0x%x>" % ( self.__class__.__name__, self.__name__, id(self) )

class ParametrizedClass( type ):
	def __call__( cls, *args, **kwargs ):
		if not hasattr( cls, '__parameters__' ):
			cls.__parameters__ = {}

			for name, value in inspect.getmembers( cls ):
				if isinstance( value, ParameterDesc ):
					value.name = name

					cls.__parameters__[ name ] = value

		return type.__call__( cls, *args, **kwargs )

class Parameter( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata, ParameterType ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',      Integer, index = True, primary_key = True ),
				Column('type_id', ForeignKey( ParameterType.id ), nullable = False ))

		cols = cls.__table__.c

		mapper( cls, cls.__table__, polymorphic_on = cols.type_id, properties = {
			'type': relation( ParameterType,
				uselist = False )
			})

	def __str__( self ):
		return '<%s@%s id="%s" type="%s">' % ( self.__origname__, self.__game__.name, self.id, self.type.name )

class ParameterType( ModelObject, ByNameMixin ):
	"""
	Object type description class.
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

__all__ = [ 'ParametrizedClass', 'ParameterDesc', 'Parameter', 'ParameterType' ]
