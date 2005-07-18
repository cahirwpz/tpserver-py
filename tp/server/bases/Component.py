
from config import db, netlib

from SQL import *

class Component(SQLBase):
	tablename = "`component`"

	def categories(self):
		"""\
		categories() -> [id, ...]

		Returns the categories the component is in.
		"""
		results = db.query("""SELECT category FROM %(tablename)s_category WHERE %(tablename)s=%(id)s""", tablename=self.tablename, id=self.id)
		return [x['category'] for x in results]

	def properties(self):
		"""\
		properties() -> [(id, value), ...]

		Returns the properties the component has.
		"""
		results = db.query("""SELECT property, value FROM %(tablename)s_property WHERE %(tablename)s=%(id)s""", tablename=self.tablename, id=self.id)
		return [(x['property'], x['value']) for x in results]

	def to_packet(self, sequence):
		return netlib.objects.Component(sequence, self.id, self.time, self.categories(), self.name, self.desc, self.requirement, self.properties())

	def id_packet(cls):
		return netlib.objects.Component_IDSequence
	id_packet = classmethod(id_packet)   

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)

