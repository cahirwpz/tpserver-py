
from config import db, netlib

from SQL import *

class Component(SQLBase):
	tablename = "`component`"
	tablename_category = "`component_category`"
	tablename_property = "`component_property`"

	def categories(self):
		"""\
		categories() -> [id, ...]

		Returns the categories the component is in.
		"""
		results = db.query("""SELECT category FROM %(tablename_category)s WHERE %(tablename)s=%(id)s""", 
			tablename_category=self.tablename_category, tablename=self.tablename, id=self.id)
		return [x['category'] for x in results]

	def properties(self):
		"""\
		properties() -> [(id, value), ...]

		Returns the properties the component has.
		"""
		results = db.query("""SELECT property, value FROM %(tablename_property)s WHERE %(tablename)s=%(id)s""", 
			tablename_property=self.tablename_property, tablename=self.tablename, id=self.id)
		return [(x['property'], x['value']) for x in results]

	def property(self, id):
		"""\
		property(property_id) -> property_value_function

		Returns the property value function for this component given a property id
		"""
		results = db.query("""SELECT value FROM %(tablename_property)s WHERE %(tablename)s=%(cid)s AND property=%(pid)s""", 
			tablename_property=self.tablename_property, tablename=self.tablename, cid=self.id, pid=id)
		if len(results) == 1:
			return results[0]['value']
		return None

	def to_packet(self, sequence):
		print (self.id, self.time, self.categories(), self.name, self.desc, self.requirements, self.properties())
		return netlib.objects.Component(sequence, self.id, self.time, self.categories(), self.name, self.desc, self.requirements, self.properties())

	def id_packet(cls):
		return netlib.objects.Component_IDSequence
	id_packet = classmethod(id_packet)   

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)

