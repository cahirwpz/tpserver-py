#!/usr/bin/env python

import sqlalchemy, datetime, re, logging

from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, scoped_session

from tp.server.singleton import SingletonClass
from tp.server.configuration import ComponentConfiguration, StringOption

# FIXME: Horrible, horrible hack!
sqlalchemy.func.current_timestamp = datetime.datetime.now

def untitle( s ):
	return "_".join( map( str.lower, filter( len, re.split( r'([A-Z][^A-Z]*)', s) ) ) )

def make_mapping( cls, *args, **kwargs ):
	metadata = DatabaseManager().metadata

	cls.__tablename__ = untitle( cls.__name__ )
	
	cls.InitMapper( metadata, *args, **kwargs )

	return cls

from sqlalchemy.interfaces import PoolListener

class ForeignKeysListener( PoolListener ):
    def connect(self, dbapi_con, con_record):
        db_cursor = dbapi_con.execute('pragma foreign_keys=ON')

from tp.server.logging import err, msg

class TwistedLogHandler( logging.Handler ):
	def createLock( self ):
		pass

	def acquire( self ):
		pass

	def release( self ):
		pass

	def close( self ):
		pass

	def emit( self, record ):
		try:
			level = record.levelname.lower()

			if level == 'info':
				level = 'debug1'
			elif level == 'debug':
				level = 'debug2'

			if record.name.startswith( 'sqlalchemy' ):
				name = ".".join( record.name.split('.')[:2] )
			else:
				name = record.name

			#for _name in dir(record):
			#	print _name, getattr( record, _name )

			if record.msg:
				msg( record.msg, system = name, level = level, time = record.created )
		except:
			err()

class DatabaseManager( object ):
	__metaclass__ = SingletonClass

	def __init__( self ):
		self.__sessionmaker = scoped_session( sessionmaker() )

	def configure( self, configuration ):
		self.engine = sqlalchemy.create_engine( configuration.database, listeners=[ ForeignKeysListener() ] )

		logger = logging.getLogger('sqlalchemy.engine')
		logger.root.addHandler( TwistedLogHandler() )
		logger.setLevel( logging.DEBUG )

		self.__sessionmaker.configure( bind = self.engine )
		self.__metadata = sqlalchemy.MetaData()
		self.__metadata.bind = self.engine

	@contextmanager
	def session( self ):
		session = self.__sessionmaker()

		try:
			yield session
		finally:
			try:
				session.commit()
			except Exception, ex:
				msg( "${yel1}%s${coff}" % ex, level='warning' )
				session.rollback()

	@property
	def metadata( self ):
		return self.__metadata

	@property
	def query( self ):
		return self.__sessionmaker().query

class DatabaseConfiguration( ComponentConfiguration ):
	component = DatabaseManager

	database = StringOption( short='D', default='sqlite:///tp.db', 
							help='Database engine supported by SQLAlchemy.', arg_name='DATABASE' )

__all__ = [ 'DatabaseManager', 'DatabaseConfiguration', 'make_mapping' ]
