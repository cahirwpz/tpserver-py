
from config import db, netlib

from SQL import *

class Design(SQLBase):
	tablename = "`design`"

	def categories(self):
		"""\
		categories() -> [id, ...]

		Returns the categories the design is in.
		"""
		results = db.query("""SELECT category FROM %(tablename)s_category WHERE %(tablename)s=%(id)s""", tablename=self.tablename, id=self.id)
		return [x['category'] for x in results]

	def valid(self):
		"""\
		valid() -> boolean

		Returns if the the design meets all the apprioate constraints.
		"""
		return True

	def used(self):
		"""\
		used() -> value

		Returns the properties (and values) a design has.
		"""
		# Need to check if the design is valid
		if not self.valid():
			return -1
		
		# FIXME: This is a bit of a hack (and most probably won't work on non-MySQL)
		results = db.query("""SELECT SUM(value) AS inplay FROM object_extra WHERE name = 'ships' AND `key` = %(key)s""", key=repr(self.id))
		try:
			inplay = result['inplay']
		except KeyError:
			inplay = 0
	
		results = db.query("""SELECT SUM(value) as beingbuilt FROM order_extra JOIN `order` ON order.id = order_extra.order WHERE name = 'ships' AND type = 'sorders.Build' AND `key` = %(key)s""", key=repr(self.id))
		try:
			beingbuilt = result['beingbuilt']
		except KeyError:
			beingbuilt = 0
		
		return inplay+beingbuilt
	
	def properties(self):
		"""\
		properties() -> [(id, value, string), ...]

		Returns the properties (and values) a design has.
		"""
		return []

	def feedback(self):
		"""\
		feedback() -> string

		Returns the feedback for this design.
		"""
		return ""

	def to_packet(self, sequence):
		# Preset arguments
		return netlib.objects.Design(sequence, self.id, self.time, self.categories(), self.name, self.desc, self.used(), self.owner, self.feedback(), self.properties())

	def id_packet(cls):
		return netlib.objects.Design_IDSequence
	id_packet = classmethod(id_packet)   

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)

