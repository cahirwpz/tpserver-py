#!/usr/bin/env python

import re, csv, datetime, inspect
from collections import Mapping
from logging import debug, info, warning, error, exception

from DatabaseManager import DatabaseManager, make_mapping

from sqlalchemy.orm import mapper
from sqlalchemy.ext.associationproxy import _AssociationCollection

def untitle( s ):
	return "_".join( map( str.lower, filter( len, re.split( r'([A-Z][^A-Z]*)', s) ) ) )

def flatten( x ):
    result = []

    for el in x:
        if hasattr( el, "__iter__") and not isinstance( el, basestring ):
            result.extend( flatten( el ) )
        else:
            result.append( el )

    return result

class Model( Mapping ):
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
		typecls = getattr( self, BaseClassName + "Type" )
		namecls = getattr( self, 'ParameterName' )

		class newcls( cls, basecls ):
			__origname__  = cls.__name__
			__tablename__ = str( "%s_%s" % ( basecls.__tablename__, untitle( cls.__name__ ) ) )
			__game__      = self.game

		newcls.__name__      = str( "%s_%s" % ( self.game.name, cls.__name__ ) )

		Model.add( namecls( name = name )
				for name in newcls.__parameters__.keys() if not namecls.ByName( name ) )

		args = tuple( self.__objects[ name ] for name in args )

		newcls_type = typecls.ByName( cls.__name__ )

		mapper( newcls, inherits = basecls, polymorphic_identity = newcls_type.id )
		
		self.__add_class( newcls.__origname__, newcls )

	def add_parameter_class( self, cls, type_id, *args ):
		metadata = DatabaseManager().metadata
		
		name = "_".join( untitle( cls.__name__ ).split('_')[0:-1] )
		
		class newcls( cls, self.Parameter ):
			__origname__  = cls.__name__
			__tablename__ = str( "%s_%s" % ( self.Parameter.__tablename__, name ) )
			__game__      = self.game

		newcls.__name__      = str( "%s_%s" % ( self.game.name, cls.__name__ ) )

		args = tuple( self.__objects[ name ] for name in args )

		newcls.InitMapper( metadata, self.Parameter, type_id, *args )
		
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
	def init():
		from Game import Game

		make_mapping( Game )

		Game.__table__.create( checkfirst = True )

	@staticmethod
	def add( *objs ):
		objs = filter( lambda x: x is not None, flatten( objs ) )

		assert all( isinstance( obj, ModelObject ) for obj in objs )
		
		with DatabaseManager().session() as session:
			for obj in objs:
				session.add( obj )

		for obj in objs:
			debug( "Added %s", obj )
	
	update = add

	@staticmethod
	def remove( *objs ):
		objs = filter( lambda x: x is not None, flatten( objs ) )

		assert all( isinstance( obj, ModelObject ) for obj in objs )

		with DatabaseManager().session() as session:
			try:
				for obj in objs:
					obj.remove( session )
			except Exception as ex:
				exception( "Removing failed: %s", ex )

	@staticmethod
	def refresh( *objs ):
		objs = filter( lambda x: x is not None, flatten( objs ) )

		assert all( isinstance( obj, ModelObject ) for obj in objs )
		
		with DatabaseManager().session() as session:
			for obj in objs:
				session.refresh( obj )

	@staticmethod
	def query( cls ):
		return DatabaseManager().query( cls )

	@staticmethod
	def create( model ):
		metadata = DatabaseManager().metadata

		tables = list( metadata.tables )

		for table in sorted( tables ):
			if table.startswith( "%s_" % model.game.name ):
				try:
					metadata.tables[ table ].create( checkfirst = True )
				except:
					error( "Cannot create storage for %s.", table )
					raise
				else:
					info( "Created storage for %s.", table )
	
	@staticmethod
	def drop( model ):
		metadata = DatabaseManager().metadata

		tables = list( metadata.tables )

		for table in sorted( tables ):
			if table.startswith( "%s_" % model.game.name ):
				metadata.tables[ table ].drop()
				del metadata.tables[ table ]
				info( "Deleted storage for %s.", table )

class ByNameMixin( object ):
	@classmethod
	def ByName( cls, name ):
		return cls.query().filter_by( name = name ).first()

class ModelObject( object ):
	def __init__( self, **kwargs ):
		self._data_descriptors = dict( inspect.getmembers( self.__class__, inspect.isdatadescriptor ) )

		for key, value in kwargs.items():
			setattr( self, key, value )
	
	def __setattr__( self, key, value ):
		if key in [ '_sa_instance_state', '_data_descriptors' ] or \
				key.startswith('_AssociationProxy') or \
				key in self._data_descriptors:
			object.__setattr__( self, key, value )
		else:
			raise AttributeError( "%s has no %s property (available properties: %s)" % \
					( self.__class__.__name__, key, ', '.join(self._data_descriptors.keys()) ))

	def remove( self, session ):
		try:
			session.delete( self )
		except Exception as ex:
			error( "Failed to remove %s: %s", self, ex )
		#else:
		#	debug( "Removed %s" % self )

	@classmethod
	def query( cls ):
		return DatabaseManager().query( cls )

	#@classmethod
	#def ByModTime( cls, filter = None ):
	#	"""
	#	ByModTime() -> cls()
	#	
	#	Gets the last modified time for the type.
	#	"""
	#	return cls.query().filter( filter ).order_by( cls.mtime ).first()

	#@classmethod
	#def ByIdRange( cls, filter = None, start = 0, amount = -1 ):
	#	"""
	#	ByIdRange( start, amount ) -> [ cls(), ...]
	#	
	#	Get the last ids for this (that the user can see).
	#	"""
	#	query = cls.query().filter( filter ).order_by( cls.mtime )
	#
	#	if amount >= 0:
	#		return query[start:(start + amount)]
	#	else:
	#		return query[start:]

	#@classmethod
	#def Count( cls, filter = None ):
	#	"""
	#	Count( filter ) -> int
	#
	#	Get the number of records in this table.
	#	"""
	#	query = cls.query()
	#
	#	if filter:
	#		query = query.filter( filter )
	#
	#	return query.count()

	@classmethod
	def ById( cls, id ):
		return cls.query().filter_by( id = id ).first()
	
	@classmethod
	def FromCSV( cls, filename ):
		with DatabaseManager().session() as session:
			reader = csv.DictReader( open( filename, "r" ) )

			for row in reader:
				obj = cls()

				for name, value in row.iteritems():
					if name is '':
						continue

					if name == 'mtime':
						value = datetime.datetime.strptime( value, "%Y-%m-%d %H:%M:%S" )

					setattr( obj, name, value )

				session.add( obj )

import sqlalchemy

or_  = sqlalchemy.or_
and_ = sqlalchemy.and_

__all__ = [ 'Model', 'ModelObject', 'ByNameMixin', 'or_', 'and_' ]
