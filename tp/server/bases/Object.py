
import db
import netlib

from SQL import *
from Order import Order

class Object(SQLWithAttrBase):
	tablename = "tp.object"
	fieldname = "object"

	def bypos(pos, size):
		"""\
		Object.bypos([x, y, z], raidus) -> [Object, ...]

		Return all objects which are centered inside a sphere centerd on
		size and radius of size.
		"""
		result = db.query("""\
			SELECT id FROM tp.object WHERE
				posx+size >= %i AND posx-size =< %i AND
				posy+size >= %i AND posy-size =< %i AND
				posz+size >= %i AND posz-size =< %i
			ORDER BY DECREASING size
		""" % (pos[0]-size, pos[1]+size, pos[1]-size, pos[1]+size, pos[2]-size, pos[2]+size))
	
		if len(result) != 1:
			return []
		else:
			r = []
			for id in result:
				r.append(Object(id=id['id']))
			return r
	bypos = staticmethod(bypos)
	
	def orders(self):
		"""\
		orders()

		Returns the number of orders this object has.
		"""
		return Order.number(self.id)

	def ordertypes(self):
		"""\
		ordertypes()

		Returns the valid order types for this object.
		"""
		results = db.query("""SELECT order_type_id FROM tp.object_order_type WHERE object_id=%(id)s""", id=self.id)
		return [x['order_type_id'] for x in results]

	def contains(self):
		"""\
		contains()

		Returns the objects this object contains.
		"""
		results = db.query("""SELECT id FROM tp.object WHERE parent=%(id)s""", id=self.id)
		return [x['id'] for x in results]

	def to_packet(self, sequence):
		# Preset arguments
		args = [sequence, self.id, self.type, self.name, self.size, self.posx, self.posy, self.posz, self.velx, self.vely, self.velz, self.contains(), [], self.orders()]
		for attribute in self.attributes():
			value = getattr(self, attribute['name'])
			args.append(value)

		packet = netlib.objects.Object(*args)
		print packet.length
		return packet

	def __str__(self):
		return "<Object type=%s id=%s>" % (self.type, self.id)

	__repr__ = __str__

