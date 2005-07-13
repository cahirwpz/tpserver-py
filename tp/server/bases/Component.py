
from config import db, netlib

from SQL import *

class Component(SQLBase):
	tablename = "`component`"

	def categories(cls, oid):
		"""\
		Component.categories(componentid) -> [id, ...]

		Returns the categories the component is in.
		"""
		results = db.query("""SELECT %(tablename)s FROM %(tablename)s_category WHERE oid=%(oid)s""", tablename=cls.tablename, oid=oid)
		return [x[cls.tablename] for x in results]
	category = classmethod(category)

	def properties(cls, oid):
		"""\
		Component.properties(componentid) -> [(id, value), ...]

		Returns the properties the component has.
		"""
		results = db.query("""SELECT %(tablename)s, value FROM %(tablename)s_property WHERE oid=%(oid)s""", tablename=cls.tablename, oid=oid)
		return [(x[cls.tablename], x['value']) for x in results]
	property = classmethod(property)

	def to_packet(self, sequence):
		# Preset arguments
		return netlib.objects.Component(sequence, self.id, self.time, self.categories(), self.name, self.desc, self.requirement, self.properties())

	def id_packet(cls):
		return netlib.objects.Component_IDSequence
	id_packet = classmethod(id_packet)   

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)

