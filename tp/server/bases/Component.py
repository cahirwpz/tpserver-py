
import pickle

from config import db, netlib

from SQL import *
from Order import Order

class Component(SQLBase):
	tablename = "`component`"
	types = {}

	def load(self, id):
		SQLBase.load(self, id)

		if len(self.language) > 0:
			self.language = pickle.loads(self.language)
		else:
			self.language = ()

	def save(self):
		if len(self.language) > 0:
			self.language = pickle.dumps(self.language)

	def used(id):
		"""\
		Component.used(id) -> integer

		Returns the number of places this component is used.
		"""
		sql = """SELECT COUNT(id) FROM %%(tablename)s WHERE base = %s ORDER BY id""" % (id)
		result = db.query(sql, tablename=Component.tablename)
		print result
		return result[0]["COUNT(id)"]
	used = staticmethod(used)

	def category(id):
		"""\
		Component.category(id) -> [1, 3]

		Returns the categories this component is a part of.
		"""
		sql = """SELECT category FROM component_category WHERE component = %s ORDER BY category""" % (id)
		result = db.query(sql, tablename=Component.tablename + "_component")
		return [x['category'] for x in result]
	category = staticmethod(category)

	def contains(id):
		"""\
		Component.contains(id) -> [1, 3]

		Returns the components contains by this component.
		"""
		sql = """SELECT * FROM component_component WHERE container = %s ORDER BY component""" % (id)
		result = db.query(sql, tablename=Component.tablename + "_component")
		return [(x['container'], x['component']) for x in result]
	contains = staticmethod(contains)

	def realid(id, pid):
		return id
	realid = staticmethod(realid)

	def all():
		results = db.query("""SELECT id FROM %(tablename)s""", tablename=Component.tablename)
		return [x['id'] for x in results]
	all = staticmethod(all)

	def next(id):
		result = db.query("""SELECT id FROM %(tablename)s WHERE id > %(id)s LIMIT 1""", tablename=Component.tablename, id=id)
		if len(results) > 0:
			return result[0]['id']
		else:
			raise NoSuch("No component after given...")
	next = staticmethod(next)

	def to_packet(self, sequence):
		print "Language:", self.language
		print "Args:", (sequence, self.id, self.base, Component.used(self.id), Component.category(self.id), self.name, self.desc, Component.contains(self.id), self.language)
		return netlib.objects.Component(sequence, self.id, self.base, Component.used(self.id), Component.category(self.id), self.name, self.desc, Component.contains(self.id), self.language)

	def __str__(self):
		return "<Component id=%s>" % (self.id,)

