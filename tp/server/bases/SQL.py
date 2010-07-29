#!/usr/bin/env python

import csv, datetime

from sqlalchemy import *
from tp.server.db import *

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
		return DatabaseManager().query( cls ).filter_by( name = name ).first()
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
	#	return DatabaseManager().query( cls ).filter( filter ).order_by( cls.mtime ).first()

	#@classmethod
	#def ByIdRange( cls, filter = None, start = 0, amount = -1 ):
	#	"""
	#	ByIdRange( start, amount ) -> [ cls(), ...]
	#	
	#	Get the last ids for this (that the user can see).
	#	"""
	#	query = DatabaseManager().query( cls ).filter( filter ).order_by( cls.mtime )
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
	#	query = DatabaseManager().query( cls )
	#
	#	if filter:
	#		query = query.filter( filter )
	#
	#	return query.count()

	@classmethod
	def ByRealId( cls, user, id ):
		"""
		ByRealId( user, id ) -> cls()
		
		Get the real id for an object (from id the user sees).
		"""
		return cls.ById( id )

	@classmethod
	def ById( cls, id ):
		return DatabaseManager().query( cls ).filter_by( id = id ).first()
	
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

__all__ = [ 'NoSuchThing', 'AlreadyExists', 'PermissionDenied', 'SQLBase', 'SelectableByName' ]
