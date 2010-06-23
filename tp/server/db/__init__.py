#!/usr/bin/env python

import sqlalchemy, datetime, re

from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, scoped_session, mapper

from tp.server.singleton import SingletonClass
from tp.server.configuration import ComponentConfiguration, StringOption

# FIXME: Horrible, horrible hack!
sqlalchemy.func.current_timestamp = datetime.datetime.now

def untitle( s ):
	return "_".join( map( str.lower, filter( len, re.split( r'([A-Z][^A-Z]*)', s) ) ) )

def make_mapping( cls, metadata, *args, **kwargs ):#{{{
	cls.__tablename__ = untitle( cls.__name__ )
	cls.__table__     = cls.getTable( cls.__tablename__, metadata, *args, **kwargs )

	mapper( cls, cls.__table__ )

	return cls
#}}}

def make_dependant_mapping( cls, metadata, game, *args, **kwargs ):#{{{
	class newcls( cls ):
		__module__    = cls.__module__
		__tablename__ = str( '%s_%s' % ( game.name, untitle( cls.__name__ ) ) )
		__table__     = cls.getTable( __tablename__, metadata, *args, **kwargs )

	newcls.__name__ = str( '%s_%s' % ( game.name, cls.__name__ ) )

	mapper( newcls, newcls.__table__ )

	return newcls
#}}}

class DatabaseManager( object ):#{{{
	__metaclass__ = SingletonClass

	def __init__( self ):
		self.__sessionmaker = scoped_session( sessionmaker() )

	def configure( self, configuration ):
		self.engine = sqlalchemy.create_engine(configuration.database)
		self.engine.echo = True
		self.__sessionmaker.configure(bind = self.engine)
		self.__metadata = sqlalchemy.MetaData()
		self.__metadata.bind = self.engine

	@contextmanager
	def session( self ):
		session = self.__sessionmaker()

		try:
			yield session
		finally:
			session.commit()

	@property
	def metadata( self ):
		return self.__metadata
#}}}

class DatabaseConfiguration( ComponentConfiguration ):#{{{
	component = DatabaseManager

	database = StringOption( short='D', default='sqlite:///tp.db', 
							help='Database engine supported by SQLAlchemy.', arg_name='DATABASE' )
#}}}

__all__ = [ 'DatabaseManager', 'DatabaseConfiguration', 'make_mapping', 'make_dependant_mapping' ]
