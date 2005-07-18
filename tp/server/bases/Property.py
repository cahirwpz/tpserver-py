
from config import db, netlib

from SQL import *

class Property(SQLBase):
	tablename = "`property`"

	def categories(self):
		"""\
		categories() -> [id, ...]

		Returns the categories the property is in.
		"""
		results = db.query("""SELECT category FROM %(tablename)s_category WHERE %(tablename)s=%(id)s""", tablename=self.tablename, id=self.id)
		return [x['category'] for x in results]

	def to_packet(self, sequence):
		# Preset arguments
		return netlib.objects.Property(sequence, self.id, self.time, self.categories(), self.rank, self.name, self.desc, self.calculate)

	def id_packet(cls):
		return netlib.objects.Property_IDSequence
	id_packet = classmethod(id_packet)   

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)

