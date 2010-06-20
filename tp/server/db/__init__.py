#!/usr/bin/env python

import sqlalchemy, datetime, re

from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, mapper

from tp.server.singleton import SingletonClass
from tp.server.configuration import ComponentConfiguration, StringOption

# FIXME: Horrible, horrible hack!
sqlalchemy.func.current_timestamp = datetime.datetime.now

def untitle( s ):
	return "_".join( map( str.lower, filter( len, re.split( r'([A-Z][^A-Z]*)', s) ) ) )

def make_mapping( cls, metadata, *args, **kwargs ):
	cls.__tablename__ = untitle( cls.__name__ )

	mapper( cls, cls.getTable( cls.__tablename__, metadata, *args, **kwargs ) )

	return cls

def make_dependant_mapping( cls, metadata, game, *args, **kwargs ):
	class newcls( cls ):
		__module__ = cls.__module__
		__tablename__ = str( '%s:%s' % ( game.name_short, untitle( cls.__name__ ) ) )

	newcls.__name__ = str( '%s_%s' % ( game.name_short, cls.__name__ ) )

	mapper( newcls, newcls.getTable( newcls.__tablename__, metadata, *args, **kwargs ) )

	return newcls

class DatabaseManager( object ):#{{{
	__metaclass__ = SingletonClass

	def __init__( self ):
		self.__sessionmaker = sessionmaker() 

	def configure( self, configuration ):
		self.engine = sqlalchemy.create_engine(configuration.database)
		self.engine.echo = True
		self.__sessionmaker.configure(bind = self.engine)

	@contextmanager
	def session( self ):
		session = self.__sessionmaker()

		try:
			yield session
		finally:
			session.commit()

	@contextmanager
	def metadata( self ):
		metadata = sqlalchemy.MetaData()
		metadata.bind = self.engine

		try:
			yield metadata
		finally:
			metadata.create_all()
#}}}

class DatabaseConfiguration( ComponentConfiguration ):#{{{
	component = DatabaseManager

	database = StringOption( short='D', default='sqlite:///tp.db', 
							help='Database engine supported by SQLAlchemy.', arg_name='DATABASE' )
#}}}

__all__ = [ 'DatabaseManager', 'DatabaseConfiguration', 'make_mapping', 'make_dependant_mapping' ]
