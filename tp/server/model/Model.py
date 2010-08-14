#!/usr/bin/env python

import re
from collections import Mapping

from SQL import SQLBase
from DatabaseManager import DatabaseManager

from sqlalchemy.orm import mapper

def untitle( s ):#{{{
	return "_".join( map( str.lower, filter( len, re.split( r'([A-Z][^A-Z]*)', s) ) ) )
#}}}

def flatten( x ):#{{{
    result = []

    for el in x:
        if hasattr( el, "__iter__") and not isinstance( el, basestring ):
            result.extend( flatten( el ) )
        else:
            result.append( el )

    return result
#}}}

class Model( Mapping ):#{{{
	def __init__( self, game ):
		self.__objects = {}
		self.game = game

	def __add_class( self, name, cls ):
		self.__objects[ name ] = cls

		setattr( self, name, cls )

	def add_class( self, cls, *args ):
		metadata = DatabaseManager().metadata

		class newcls( cls ):
			__origname__  = cls.__name__
			__module__    = cls.__module__
			__tablename__ = "_".join( [ self.game.name, untitle( cls.__name__ ) ] )
			__game__      = self.game
		
		newcls.__name__  = str( '%s_%s' % ( self.game.name, cls.__name__ ) )

		args = tuple( self.__objects[ name ] for name in args )

		newcls.InitMapper( metadata, *args )

		self.__add_class( cls.__name__, newcls )

	def add_object_class( self, cls, *args ):
		self.add_parametrized_class( cls, 'Object', *args )

	def add_order_class( self, cls, *args ):
		self.add_parametrized_class( cls, 'Order', *args )

	def add_parametrized_class( self, cls, BaseClassName, *args ):
		basecls = getattr( self, BaseClassName )
		typecls  = getattr( self, BaseClassName + "Type" )

		class newcls( cls, basecls ):
			__origname__  = cls.__name__
			__tablename__ = str( "%s_%s" % ( basecls.__tablename__, untitle( cls.__name__ ) ) )
			__game__      = self.game

		newcls.__name__      = str( "%s_%s" % ( self.game.name, cls.__name__ ) )

		args = tuple( self.__objects[ name ] for name in args )

		newcls_type = typecls.ByName( cls.__name__ )

		mapper( newcls, inherits = basecls, polymorphic_identity = newcls_type.id )
		
		self.__add_class( newcls.__origname__, newcls )

	def add_parameter_class( self, cls, *args ):
		metadata = DatabaseManager().metadata
		
		name = "_".join( untitle( cls.__name__ ).split('_')[0:-1] )
		
		class newcls( cls, self.Parameter ):
			__origname__  = cls.__name__
			__tablename__ = str( "%s_%s" % ( self.Parameter.__tablename__, name ) )
			__game__      = self.game

		newcls.__name__      = str( "%s_%s" % ( self.game.name, cls.__name__ ) )

		args = tuple( self.__objects[ name ] for name in args )

		newcls.InitMapper( metadata, self.Parameter, *args )
		
		self.__add_class( newcls.__origname__, newcls )

	def use( self, *names ):
		if len( names ) == 1:
			return self.__objects[ names[0] ]
		else:
			return tuple( self.__objects[ name ] for name in names )

	def __getitem__( self, name ):
		return self.__objects[ name ]

	def __len__( self ):
		return self.__objects.__len__()

	def __iter__( self ):
		return self.__objects.__iter__()

	@staticmethod
	def add( *objs ):
		objs = filter( lambda x: x is not None, flatten( objs ) )

		assert all( isinstance( obj, SQLBase ) for obj in objs )
		
		with DatabaseManager().session() as session:
			for obj in objs:
				session.add( obj )
	
	update = add

	@staticmethod
	def remove( *objs ):
		objs = filter( lambda x: x is not None, flatten( objs ) )

		assert all( isinstance( obj, SQLBase ) for obj in objs )

		with DatabaseManager().session() as session:
			for obj in objs:
				obj.remove( session )

	@staticmethod
	def refresh( *objs ):
		objs = filter( lambda x: x is not None, flatten( objs ) )

		assert all( isinstance( obj, SQLBase ) for obj in objs )
		
		with DatabaseManager().session() as session:
			for obj in objs:
				session.refresh( obj )

	@staticmethod
	def query( cls ):
		return DatabaseManager().query( cls )
#}}}

import sqlalchemy

or_  = sqlalchemy.or_
and_ = sqlalchemy.and_

__all__ = [ 'Model', 'or_', 'and_' ]
