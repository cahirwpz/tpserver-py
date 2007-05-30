
import sqlalchemy as sql

class Proxy(object):
	def __init__(self):
		self.engine = None
		self.game   = None

	def select(self, *a, **kw):
		r = sql.select(*a, **kw)
		def execute(self=r, proxy=self, **arguments):
			if proxy.game != None:
				for table in self.froms:
					# FIXME: Horrible hack!
					if table.fullname == "game":
						continue

					self.append_whereclause((table.c.game == proxy.game))
			return self._execute(**arguments)

		r._execute = r.execute
		r.execute = execute

		return r

	def insert(self, *a, **kw):
		r = sql.insert(*a, **kw)
		def execute(self=r, proxy=self, **arguments):
			if not proxy.game is None:
				arguments['game'] = proxy.game
			return self._execute(**arguments)

		r._execute = r.execute
		r.execute = execute

		return r

	def update(self, *a, **kw):
		r = sql.update(*a, **kw)
		def execute(self=r, proxy=self, **arguments):
			if not proxy.game is None:
				arguments['game'] = proxy.game
			return self._execute(**arguments)

		r._execute = r.execute
		r.execute = execute

		return r

	def delete(self, *a, **kw):
		r = sql.delete(*a, **kw)
		def execute(self=r, proxy=self, **arguments):
			if not proxy.game is None:
				self.whereclause &= (self.table.c.game == proxy.game)
			return self._execute(**arguments)

		r._execute = r.execute
		r.execute  = execute
		
		return r

	def use(self, db=None):
		# Clear the old value
		old = self.game
		self.game = None

		if db != None:
			from tp.server.bases.Game import Game
			if isinstance(db, Game):
				self.game = db.id
			elif isinstance(db, (str, unicode)):
				self.game = Game.gameid(db)
			elif isinstance(db, int):
				self.game = db
			else:
				raise SyntaxError("dbconn.use called with a weird argument %s" % db)

		# Return the previous value...
		return old

	def __getattr__(self, name):
		if self.engine is None:
			raise AttributeError("No such attribute %s" % name)
		return getattr(self.engine, name)

dbconn = Proxy()
select = dbconn.select
insert = dbconn.insert
update = dbconn.update
delete = dbconn.delete

def setup(dbconfig, echo=False):
	engine = sql.create_engine(dbconfig, strategy='threadlocal')
	sql.default_metadata.connect(engine)
	sql.default_metadata.engine.echo = echo
	
	sql.default_metadata.create_all()

	dbconn.engine = sql.default_metadata.engine
