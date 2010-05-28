import sqlalchemy, datetime, logging
from sqlalchemy.orm import sessionmaker

from tp.server.configuration import ComponentConfiguration, StringOption

# FIXME: Horrible, horrible hack!
sqlalchemy.func.current_timestamp = datetime.datetime.now

from tp.server.singleton import SingletonClass

class DatabaseManager( object ):
	__metaclass__ = SingletonClass

	def __init__( self ):
		self.metadata = sqlalchemy.MetaData()
		self.session = sessionmaker() 

		globals()['metadata'] = self.metadata

	def configure( self, configuration ):
		self.engine = sqlalchemy.create_engine(configuration.database, strategy='threadlocal')
		self.engine.echo = True
		self.metadata.bind = self.engine
		self.metadata.create_all()
		self.session.configure(bind = self.engine)

class DatabaseConfiguration( ComponentConfiguration ):#{{{
	component = DatabaseManager

	database = StringOption( short='D', default='sqlite:///tp.db', 
							help='Database engine supported by SQLAlchemy.', arg_name='DATABASE' )
#}}}

