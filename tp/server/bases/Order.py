
import netlib
from config import db

from SQL import *

class Order(SQLTypedBase):
	tablename = "tp.order"
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

	def desc_packet(sequence, typeno):
		"""\
		Order.desc_packet(sequence, typeno)

		Builds an order description packet for the specified order type.
		"""
		# Pull out the arguments
		if not Order.types.has_key(typeno):
			raise NoSuch("No such order type.")

		order = Order(typeno=typeno)
		
		arguments = []
		for attribute in order.attributes.values():
			if attribute.level != 'private':
				arguments.append((attribute.name, attribute.type, attribute.desc))
		return netlib.objects.OrderDesc(sequence, typeno, order.__class__.__name__, order.__class__.__doc__, arguments)
	desc_packet = staticmethod(desc_packet)
	
	def load_all():
		"""\
		Order.load_all()

		Loads all the possible order types from the database.
		"""
		for id in Order.types.keys():
			Order.desc_packet(0, id).register()
	load_all = staticmethod(load_all)

	def __init__(self, oid=None, slot=None, packet=None, type=None, typeno=None, id=None):
		if oid != None and slot != None:
			id = self.realid(oid, slot)
		else:
			id = None
			
		SQLTypedBase.__init__(self, id, packet, type, typeno)
	
	def object(self):
		if not hasattr(self, "_object"):
			from Object import Object
			self._object = Object(self.oid)
		return self._object
	object = property(object)

	def insert(self):
		try:
			db.query("BEGIN")
		
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

		except Exception, e:
			db.query("ROLLBACK")
			raise e
		else:
			db.query("COMMIT")

	def save(self):
		if not hasattr(self, 'id'):
			id = self.realid(self.oid, self.slot)
			if id != -1:
				self.id = id
		SQLTypedBase.save(self)

	def remove(self):
		try:
			db.query("BEGIN")
			
			# Move the other orders down
			db.query("""UPDATE tp.order SET slot=slot-1 WHERE slot>=%(slot)s AND oid=%(oid)s""", self.todict())
			SQLTypedBase.remove(self)

		except Exception, e:
			db.query("ROLLBACK")
		else:
			db.query("COMMIT")

	def to_packet(self, sequence):
		# Preset arguments
		args = [sequence, self.oid, self.slot, self.typeno, self.turns(), self.resources()]
		SQLTypedBase.to_packet(self, sequence, args)
		return netlib.objects.Order(*args)

	def from_packet(self, packet):
		self.worked = 0

		self.oid = packet.id
		self.slot = packet.slot
		SQLTypedBase.from_packet(self, packet)

		del self.id

	def __str__(self):
		if hasattr(self, 'id'):
			return "<Order type=%s id=%s oid=%s slot=%s>" % (self.typeno, self.id, self.oid, self.slot)
		else:
			return "<Order type=%s id=XX oid=%s slot=%s>" % (self.typeno, self.oid, self.slot)

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
		
