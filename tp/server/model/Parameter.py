#!/usr/bin/env python

import inspect

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, class_mapper
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from Model import ModelObject
from Generic import NameMap

class ParameterDesc( object ):
	def __init__( self, type, level, default = None, description = None ):
		self.type			= type
		self.level			= level
		self.default		= default
		self.description	= description

		if hasattr( self.type, '__maps_to__' ):
			self.getter = lambda obj: getattr( obj.parameters[ self.name ], self.type.__maps_to__ )
			self.setter = lambda obj, value: setattr( obj.parameters[ self.name ], self.type.__maps_to__, value )
		else:
			self.getter = lambda obj: obj.parameters.get( self.name )
			self.setter = lambda obj, value: obj.parameters.set( self.name, value )

	def __check( self, obj ):
		try:
			obj.parameters[ self.name ]
		except KeyError:
			obj.parameters[ self.name ] = obj.__game__.model.use( self.type.__name__ )()

	def __get__( self, obj, objtype ):
		if obj is None:
			return self

		self.__check( obj )

		return self.getter( obj )

	def __set__( self, obj, value ):
		if value is not None:
			self.__check( obj )

			self.setter( obj, value )
	
	def __str__( self ):
		if not self.__name__:
			return "<%s object at 0x%x>" % ( self.__class__.__name__, id(self) )
		else:
			return "<%s \'%s\' object at 0x%x>" % ( self.__class__.__name__, self.__name__, id(self) )

class ParametrizedClass( type ):
	def __init__( cls, *args, **kwargs ):
		if not hasattr( cls, '__parameters__' ):
			cls.__parameters__ = {}

			for name, value in inspect.getmembers( cls ):
				if isinstance( value, ParameterDesc ):
					value.name = name

					cls.__parameters__[ name ] = value

		return type.__init__( cls, *args, **kwargs )

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

class AddedParameter( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata, Subject, Parameter, ParameterName ):
		subject = Subject.__origname__.lower()

		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('%s_id' % subject, ForeignKey( Subject.id ), index = True, primary_key = True ),
				Column('name_id',  ForeignKey( ParameterName.id ), index = True, primary_key = True ),
				Column('param_id', ForeignKey( Parameter.id ), nullable = True ))

		mapper( cls, cls.__table__, properties = {
			'_name' : relation( ParameterName,
				uselist = False ),
			'parameter' : relation( Parameter,
				uselist = False )
			})

		cls.name = property( 
			lambda self: getattr( self._name, 'name', None ),
			lambda self, name: setattr( self, '_name', ParameterName.ByName(name) ) )

		class_mapper( Subject ).add_property( '_parameters',
			relation( cls, collection_class = attribute_mapped_collection('name') ))

		Subject.parameters = association_proxy('_parameters', 'parameter', creator = lambda k, v: cls( name = k, parameter = v ) )

	def remove( self, session ):
		self.parameter.remove( session )

		session.delete( self )

class ParameterType( NameMap ):
	"""
	Parameter type description class.
	"""

class ParameterName( NameMap ):
	"""
	Parameter name description class.
	"""

__all__ = [ 'ParametrizedClass', 'ParameterDesc', 'Parameter', 'ParameterType', 'ParameterName', 'AddedParameter' ]
