
from config import db, netlib

from SQL import *

class Category(SQLBase):
	tablename = "`category`"

	def realid(id, pid):
		return id
	realid = staticmethod(realid)

	def all():
		results = db.query("""SELECT id FROM %(tablename)s""", tablename=Category.tablename)
		return [x['id'] for x in results]
	all = staticmethod(all)

	def next(id):
		result = db.query("""SELECT id FROM %(tablename)s WHERE id > %(id)s LIMIT 1""", tablename=Message.tablename, id=id)
		if len(results) > 0:
			return result[0]['id']
		else:
			raise NoSuch("No category after given...")
	next = staticmethod(next)

	def to_packet(self, sequence):
		# Preset arguments
		return netlib.objects.Category(sequence, self.id, self.name, self.desc)

	def __str__(self):
		return "<Category id=%s name=%s>" % (self.id, self.name)

