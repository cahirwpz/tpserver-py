
import sqlalchemy as sql

class Executor(object):
	def __init__(self, proxy, query):
		self.proxy = proxy

		self.query     = query
		query._execute = query.execute
		query.execute  = self

	def __call__(self, *args, **kw):
		raise SyntaxError("__adapt__ method not implimented")

class SelectExecutor(Executor):
	def __call__(self, *args, **kw):
		query = self.query
		proxy = self.proxy

		if proxy.game != None:
			for table in query.froms:
				if isinstance(table, sql.Table):
					# FIXME: Horrible hack!
					if table.fullname == "game":
						continue

					query.append_whereclause((table.c.game == proxy.game))
				elif isinstance(table, sql.Join):
					for table in set(table._get_from_objects()[1:]):
						# FIXME: Horrible hack!
						if table.fullname == "game":
							continue

						query.append_whereclause((table.c.game == proxy.game))

		return query._execute(*args, **kw)

class UpdateDeleteExecutor(Executor):
	def __call__(self, *args, **kw):
		query = self.query
		proxy = self.proxy

		if not proxy.game is None:
			whereclause = (query.table.c.game == proxy.game)
			if not query.whereclause is None:
				whereclause &= query.whereclause

			query.whereclause = whereclause
		return query._execute(*args, **kw)

UpdateExecutor = UpdateDeleteExecutor
DeleteExecutor = UpdateDeleteExecutor

class InsertExecutor(Executor):
	def __call__(self, *args, **kw):
		query = self.query
		proxy = self.proxy

		if not proxy.game is None:
			kw['game'] = proxy.game
		return query._execute(*args, **kw)

class Proxy(object):
	def __init__(self):
		self.engine = None
		self.game   = None

	def select(self, *a, **kw):
		exe = SelectExecutor(self, sql.select(*a, **kw))
		return exe.query 

	def insert(self, *a, **kw):
		exe = InsertExecutor(self, sql.insert(*a, **kw))
		return exe.query 

	def update(self, *a, **kw):
		exe = UpdateExecutor(self, sql.update(*a, **kw))
		return exe.query 

	def delete(self, *a, **kw):
		exe = DeleteExecutor(self, sql.delete(*a, **kw))
		return exe.query 

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


mapping = {
	sql.Integer  : int,
}
def convert(column, value):
	try:
		return mapping[column.type](value)
	except KeyError:
		return value

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
