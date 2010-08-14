#!/usr/bin/env python

import csv, datetime

import sqlalchemy as sql
from sqlalchemy import *
from DatabaseManager import DatabaseManager

class NoSuchThing( Exception ):#{{{
	pass
#}}}

class AlreadyExists( Exception ):#{{{
	pass
#}}}

class PermissionDenied( Exception ):#{{{
	pass
#}}}

class SelectableByName( object ):#{{{
	@classmethod
	def ByName( cls, name ):
		return cls.query().filter_by( name = name ).first()
#}}}

class Enum( sql.types.Unicode ):#{{{
	def __init__( self, values, empty_to_none = False ):      
		"""
		contruct an Enum type

		values : a list of values that are valid for this column
		empty_to_none : treat the empty string '' as None
		"""
		if values is None or len(values) is 0:
			raise exceptions.AssertionError('Enum requires a list of values')

		self.empty_to_none = empty_to_none
		self.values = values

		# the length of the string/unicode column should be the longest string
		# in values
		size = max( len(v) for v in values if v is not None )

		super( Enum, self ).__init__( size )

	def convert_bind_param( self, value, engine ):
		if self.empty_to_none and value is '':
			value = None

		if value not in self.values:
			raise exceptions.AssertionError( '"%s" not in Enum.values' % value )

		return super( Enum, self ).convert_bind_param( value, engine )

	def convert_result_value( self, value, engine ):
		if value not in self.values:
			raise exceptions.AssertionError( '"%s" not in Enum.values' % value )

		return super( Enum, self ).convert_result_value( value, engine )
#}}}

class SQLBase( object ):#{{{
	def __init__( self, **kwargs ):
		for key, value in kwargs.items():
			if key in self._sa_instance_state.manager.local_attrs:
				object.__setattr__( self, key, value )
				continue

			if hasattr( self, '__parameters__' ):
				if key in self.__parameters__:
					object.__setattr__( self, key, value )
					continue


			print self.__class__.__name__
			print "  dictionary:", dir(self)
			if hasattr( self, '__parameters' ):
				print "  parameters:", self.__parameters__

			raise AttributeError( "%s has no %s column / property" % ( self.__class__.__name__, key ) )
	
	def __setattr__( self, key, value ):
		if key is not '_sa_instance_state':
			attrs = list( self.__dict__ )

			if hasattr( self, '_sa_instance_state' ):
				attrs += list( self._sa_instance_state.manager.local_attrs )

			if key not in attrs:
				print( "%s has no %s attribute" % ( self.__class__.__name__, key ) )

		object.__setattr__( self, key, value )

	def remove( self, session ):
		session.delete( self )

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
#}}}

__all__ = [ 'NoSuchThing', 'AlreadyExists', 'PermissionDenied', 'Enum', 'SQLBase', 'SelectableByName' ]
