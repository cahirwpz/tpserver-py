#!/usr/bin/env python

import csv, datetime

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
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

			if hasattr( self, '__attributes__' ):
				if key in self.__attributes__:
					object.__setattr__( self, key, value )
					continue

			print dir(self)
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
	def ByModTime( cls, user = None ):
		"""
		ByModTime() -> cls()
		
		Gets the last modified time for the type.
		"""
		return DatabaseManager().query( cls ).order_by( cls.__table__.c.mtime ).first()

	@classmethod
	def ByIdRange( cls, user = None, start = 0, amount = -1 ):
		"""
		ByIdRange( start, amount ) -> [ cls(), ...]
		
		Get the last ids for this (that the user can see).
		"""
		if amount >= 0:
			end = start + 1
		else:
			end = -1

		return DatabaseManager().query( cls ).order_by( cls.__table__.c.mtime )[start:amount]

	@classmethod
	def Count( cls, user = None ):
		"""
		Count( user ) -> int

		Get the number of records in this table (that the user can see).
		"""
		return DatabaseManager().query( cls ).count()

	@classmethod
	def ByRealId( cls, user, id ):
		"""
		ByRealId( user, id ) -> cls()
		
		Get the real id for an object (from id the user sees).
		"""
		return cls.ById( id )

	@classmethod
	def ById( cls, id ):
		result = DatabaseManager().query( cls ).filter_by( id = id ).first()

		if result is None:
			raise NoSuchThing

		return result
	
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

class GenericList( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Item ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',      Integer, index = True, primary_key = True ),
				Column('item_id', ForeignKey( Item.id ), index = True, primary_key = True ))

		mapper( cls, cls.__table__, properties = {
			'item' : relation( Item,
				uselist = False,
				cascade = 'all' )
			})
#}}}

__all__ = [ 'NoSuchThing', 'AlreadyExists', 'PermissionDenied', 'SQLBase', 'SelectableByName', 'GenericList' ]
