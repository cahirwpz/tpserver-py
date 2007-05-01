
import sqlalchemy as sql

class Proxy(object):
	def __init__(self):
		self.engine = None
		self.game   = None

	def select(self, *a, **kw):
		print "Creating a select statment"

		r = sql.select(*a, **kw)
		def execute(self=r, proxy=self, **arguments):
			print "Executing a select statement!"
			if proxy.game == None:
				return query.execute(**kw)

			for table in self.froms:
				print "Table", table
				self.append_whereclause((table.c.game == proxy.game))
			return self._execute(**arguments)

		r._execute = r.execute
		r.execute = execute

		return r

	def insert(self, *a, **kw):
		print "Creating a insert statment"

		r = sql.insert(*a, **kw)
		def execute(self=r, proxy=self, **arguments):
			print "Executing a insert statement!"
			if not proxy.game is None:
				arguments['game'] = proxy.game
			return self._execute(**arguments)

		r._execute = r.execute
		r.execute = execute

		return r

	def update(self, *a, **kw):
		print "Creating a update statment"

		r = sql.update(*a, **kw)
		def execute(self=r, proxy=self, **arguments):
			print "Executing a update statement!"
			if not proxy.game is None:
				arguments['game'] = proxy.game
			return self._execute(**arguments)

		r._execute = r.execute
		r.execute = execute

		return r

	def delete(self, *a, **kw):
		print "Creating a delete statment"

		r = sql.delete(*a, **kw)
		def execute(self=r, proxy=self, **arguments):
			print "Executing a delete statement!"
			if not proxy.game is None:
				self.whereclause &= (self.table.c.game == proxy.game)
			return self._execute(**arguments)

		r._execute = r.execute
		r.execute = execute
		
		return r

	def use(self, db=None):
		# FIXME: This should look the game ID up in a table
		self.game = int(db)

	def __getattr__(self, name):
		if self.engine is None:
			raise AttributeError("No such attribute %s" % name)
		return getattr(self.engine, name)

dbconn = Proxy()
select = dbconn.select
insert = dbconn.insert
update = dbconn.update
delete = dbconn.delete

def setup(dbconfig):
	engine = sql.create_engine(dbconfig, strategy='threadlocal')
	sql.default_metadata.connect(engine)
	sql.default_metadata.engine.echo = True
	sql.default_metadata.create_all()

	dbconn.engine = sql.default_metadata.engine
