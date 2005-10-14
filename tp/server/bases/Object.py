
from config import db, netlib, admin

from SQL import *
from Order import Order

class Object(SQLTypedBase):
	tablename = "`object`"
	tablename_extra = "`object_extra`"
	types = {}

	orderclasses = {}

	def bypos(cls, pos, size=0, limit=-1, orderby="time, size DESC"):
		"""\
		Object.bypos([x, y, z], size) -> [Object, ...]

		Return all objects which are centered inside a sphere centerd on
		size and radius of size.
		"""
		pos = long(pos[0]), long(pos[1]), long(pos[2])
		
		sql = """\
SELECT id, time FROM %%(tablename)s WHERE \
	(pow(posx-%s, 2) + pow(posy-%s, 2) + pow(posz-%s, 2)) <= ( %s + pow(size, 2) ) \
ORDER BY %s \
		""" % (pos[0], pos[1], pos[2], size**2, orderby)
		if limit != -1:
			sql += "LIMIT %s" % limit

		results = db.query(sql, tablename=cls.tablename)
		return [(x['id'], x['time']) for x in results]
	bypos = classmethod(bypos)

	def byparent(cls, id):
		"""\
		byparent(id)

		Returns the objects which have a parent of this id.
		"""
		results = db.query("""SELECT id, time FROM %(tablename)s WHERE parent=%(id)s""", tablename=cls.tablename, id=id)
		return [(x['id'], x['time']) for x in results]
	byparent = classmethod(byparent)

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

	def protect(self, user):
		o = SQLBase.protect(self, user)
		if not (user.id in admin) and (hasattr(self, "owner") and self.owner != user.id):
			def empty():
				return 0
			o.orders = empty

		return o

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
		"""
		contains()

		Returns the objects which this object contains.
		"""
		ids = self.byparent(self.id)
		if len(ids) > 0:
			return zip(*ids)[0]
		else:
			return tuple()

	def to_packet(self, sequence):
		# Preset arguments
		args = [sequence, self.id, self.typeno, self.name, self.size, self.posx, self.posy, self.posz, self.velx, self.vely, self.velz, self.contains(), self.ordertypes(), self.orders(), self.time]
		SQLTypedBase.to_packet(self, sequence, args)
		return netlib.objects.Object(*args)

	def id_packet(cls):
		return netlib.objects.Object_IDSequence
	id_packet = classmethod(id_packet)

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
