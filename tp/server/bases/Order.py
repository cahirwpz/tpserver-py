
import db
import netlib

from SQL import *

class Order(SQLWithAttrBase):
	tablename = "tp.order"
	fieldname = "order"

	types = {}

	def realid(oid, slot):
		"""\
		Order.realid(objectid, slot) -> id
		
		Returns the database id for the order found on object at slot.
		"""
		result = db.query("""SELECT id FROM tp.order WHERE oid=%(oid)s and slot=%(slot)s""", oid=oid, slot=slot)
		if len(result) != 1:
			return -1
		else:
			return result[0]['id']
	realid = staticmethod(realid)

	def number(oid):
		"""\
		Order.number(objectid) -> number

		Returns the number of orders on an object.
		"""
		return db.query("""SELECT count(id) FROM tp.order WHERE oid=%(oid)s""", oid=oid)[0]['count(id)']
	number = staticmethod(number)

	def desc_packet(sequence, type):
		"""\
		Order.desc_packet(sequence, type)

		Builds an order description packet for the specified order type.
		"""
		# Pull out the arguments
		order = Order(type=type)
		
		arguments = []
		for attribute in order.attributes.values():
			if attribute.level != 'private':
				arguments.append((attribute.name, attribute.type, attribute.desc))

		results = db.query("""SELECT * FROM order_type WHERE id=%s""" % type)
		if len(results) != 1:
			raise NoSuch("No such type of order.")
		result = results[0]
		
		return netlib.objects.OrderDesc(sequence, type, result['name'], result['desc'], arguments)
	desc_packet = staticmethod(desc_packet)
	
	def load_all():
		"""\
		Order.load_all()

		Loads all the possible order types from the database.
		"""
		results = db.query("""SELECT id FROM order_type WHERE id >= 0""")
		for result in results:
			Order.desc_packet(0, result['id']).register()
	load_all = staticmethod(load_all)

	def object(self):
		if not hasattr(self, "_object"):
			from Object import Object
			self._object = Object(self.oid)
		return self._object
	object = property(object)

	def __init__(self, oid=None, slot=None, packet=None, type=None, id=None):
	
		if oid != None and slot != None:
			id = self.realid(oid, slot)
		else:
			id = None
			
		SQLWithAttrBase.__init__(self, id, packet, type)

	def insert(self):
		number = self.number(self.oid)
		if self.slot == -1:
			self.slot = number
		elif self.slot <= number:
			# Need to move all the other orders down
			print self.todict()
			db.query("""UPDATE tp.order SET slot=slot+1 WHERE slot>=%(slot)s AND oid=%(oid)s""" % self.todict())
		else:
			raise NoSuch("Cannot insert to that slot number.")
		
		self.save()

	def save(self):
		if not hasattr(self, 'id'):
			id = self.realid(self.oid, self.slot)
			if id != -1:
				self.id = id
		SQLWithAttrBase.save(self)

	def remove(self):
		# Move the other orders down
		db.query("""UPDATE tp.order SET slot=slot-1 WHERE slot>=%(slot)s AND oid=%(oid)s""", self.todict())

		SQLWithAttrBase.remove(self)

	def to_packet(self, sequence):
		# Preset arguments
		args = [sequence, self.oid, self.slot, self.type, self.turns(), self.resources()]
		SQLWithAttrBase.to_packet(self, sequence, args)
		return netlib.objects.Order(*args)

	def from_packet(self, packet):
		SQLWithAttrBase.from_packet(self, packet)

		self.oid = self.id
		del self.id

	def __str__(self):
		return "<Order type=%s id=%s oid=%s slot=%s>" % (self.type, self.id, self.oid, self.slot)

	def turns(self, turns=0):
		"""\
		Number of turns this order will take to complete.
		"""
		return turns + 0
	
	def resources(self):
		"""\
		The resources this order will consume/use. (Negative for producing).
		"""
		return []
		
# Figure out the types
class OrderTypes:
	pass
for row in db.query("""SELECT name, id FROM tp.order_type"""):
	setattr(OrderTypes, row['name'], row['id'])
