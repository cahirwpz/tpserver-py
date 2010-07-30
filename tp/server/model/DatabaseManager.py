#!/usr/bin/env python

import sqlalchemy, datetime, re

from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, scoped_session

from tp.server.singleton import SingletonClass
from tp.server.configuration import ComponentConfiguration, StringOption

# FIXME: Horrible, horrible hack!
sqlalchemy.func.current_timestamp = datetime.datetime.now

def untitle( s ):
	return "_".join( map( str.lower, filter( len, re.split( r'([A-Z][^A-Z]*)', s) ) ) )

def make_mapping( cls, *args, **kwargs ):#{{{
	metadata = DatabaseManager().metadata

	cls.__tablename__ = untitle( cls.__name__ )
	
	cls.InitMapper( metadata, *args, **kwargs )

	return cls
#}}}

from sqlalchemy.interfaces import PoolListener

class ForeignKeysListener( PoolListener ):#{{{
    def connect(self, dbapi_con, con_record):
        db_cursor = dbapi_con.execute('pragma foreign_keys=ON')
#}}}

class DatabaseManager( object ):#{{{
	__metaclass__ = SingletonClass

	def __init__( self ):
		self.__sessionmaker = scoped_session( sessionmaker() )

	def configure( self, configuration ):
		self.engine = sqlalchemy.create_engine( configuration.database, listeners=[ ForeignKeysListener() ] )
		self.engine.echo = True
		self.__sessionmaker.configure( bind = self.engine )
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

	@property
	def query( self ):
		return self.__sessionmaker().query
#}}}

class DatabaseConfiguration( ComponentConfiguration ):#{{{
	component = DatabaseManager

	database = StringOption( short='D', default='sqlite:///tp.db', 
							help='Database engine supported by SQLAlchemy.', arg_name='DATABASE' )
#}}}

__all__ = [ 'DatabaseManager', 'DatabaseConfiguration', 'make_mapping' ]
