
from sqlalchemy import *

class Proxy(object):
	def __init__(self):
		self.__dict__['game'] = None
		self.__dict__['engine'] = None
		self.__dict__['dbconn'] = None

	def __getattr__(self, key, ignore=False):
		if not self.__dict__.has_key(key) or ignore:
			if self.__dict__['dbconn'] is None:
				return getattr(self.__dict__['engine'], key)
			else:
				return getattr(self.__dict__['dbconn'], key)
		return self.__dict__[key]

	def begin(self, *args, **kw):
		if self.dbconn is None:
			self.dbconn = self.engine.connect()
			self.dbconn.first = True

		trans = self.dbconn.begin(*args, **kw)
		trans.previous = self.dbconn
		return trans

	def rollback(self, *args, **kw):
		r = self.dbconn.rollback(*args, **kw)

		self.dbconn = self.dbconn.previous
		if hasattr(self.dbconn, 'first'):
			self.dbconn = None

		return r

	def commit(self, *args, **kw):
		r = self.dbconn.commit(*args, **kw)
		self.dbconn = self.dbconn.previous
		if hasattr(self.dbconn, 'first'):
			self.dbconn = None
		return r

	def execute(self, obj, **kw):
		if False and self.game == None:
			return self.__getattr__('execute', True)(obj, **kw)
		else:
			# Add the gameid to the select...
			if isinstance(obj, (sql.Select, sql._Delete, sql._Update)):
				print "Going to do a select, delete or update!"
			elif isinstance(obj, sql._Insert):
				print "Going to do insert!"
			else:
				print "Dunno what this is?"
			print self, repr(obj), kw
			return self.__getattr__('execute', True)(obj, **kw)

dbconn = Proxy()
def setup(dbconfig):
	global_connect(dbconfig)
	default_metadata.engine.echo = True
	default_metadata.create_all()

	dbconn.engine = default_metadata.engine

