
from config import db, netlib

from SQL import *
from Order import Order

class Object(SQLTypedBase):
	tablename = "`object`"
	types = {}

	orderclasses = {}

	def bypos(pos, size=0, limit=-1):
		"""\
		Object.bypos([x, y, z], size) -> [Object, ...]

		Return all objects which are centered inside a sphere centerd on
		size and radius of size.
		"""
		pos = long(pos[0]), long(pos[1]), long(pos[2])
		
		# FIXME: This is a square...
		sql = """\
SELECT * FROM %%(tablename)s WHERE \
      (%s <= posx+size AND %s >= posx-size) AND \
      (%s <= posy+size AND %s >= posy-size) AND \
      (%s <= posz+size AND %s >= posz-size) \
ORDER BY size
		""" % (pos[0]-size, pos[0]+size, pos[1]-size, pos[1]+size, pos[2]-size, pos[2]+size)
		if limit != -1:
			sql += "LIMIT %s" % limit

		result = db.query(sql, tablename=Object.tablename)
		r = []
		for id in result:
			r.append(Object(id=id['id']))
		return r
	bypos = staticmethod(bypos)

	def realid(oid, pid):
		return oid
	realid = staticmethod(realid)

	def __init__(self, id=None, packet=None, type=None, typeno=None):
		self.name = "Unknown object"
		self.size = 0
		self.posx = 0
		self.posy = 0
		self.posz = 0
		self.velx = 0
		self.vely = 0
		self.velz = 0
		self.parent = 0

		SQLTypedBase.__init__(self, id, packet, type, typeno)
	
	def remove(self):
		# FIXME: Need to remove associated orders in a better way
		db.query("""DELETE FROM %(tablename)s WHERE oid=%(id)s""", tablename=Order.tablename, id=self.id)
		# Remove any parenting on this object.
		db.query("""UPDATE %(tablename)s SET parent=0 WHERE parent=%(id)s""", self.todict())
		SQLTypedBase.remove(self)
	
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
		if not hasattr(self, "_ordertypes"):
			self._ordertypes = []
			for type in self.orderclasses:
				self._ordertypes.append(quickimport(type).typeno)
		
		return self._ordertypes

	def contains(self):
		"""\
		contains()

		Returns the objects this object contains.
		"""
		results = db.query("""SELECT id FROM %(tablename)s WHERE parent=%(id)s""", self.todict())
		return [x['id'] for x in results]

	def to_packet(self, sequence):
		# Preset arguments
		args = [sequence, self.id, self.typeno, self.name, self.size, self.posx, self.posy, self.posz, self.velx, self.vely, self.velz, self.contains(), self.ordertypes(), self.orders()]
		SQLTypedBase.to_packet(self, sequence, args)
		return netlib.objects.Object(*args)

	def __str__(self):
		return "<Object type=%s id=%s>" % (self.typeno, self.id)

	def ghost(self):
		"""\
		Returns true if this object should be removed.
		"""
		if hasattr(self, "owner"):
			return self.owner == 0
		else:
			return False
