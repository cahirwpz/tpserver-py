
try:
	import cPickle as pickle
except ImportError:
	import pickle

import db

class NoSuch(Exception):
	pass

class SQLBase(object):
	def description(self):
		"""\
		*Internal*

		Get a description of the object.
		"""
		if not hasattr(self, "_description"):
			self._description = db.query("DESCRIBE %(tablename)s", tablename=self.tablename)
		return self._description
	description = property(description)

	def __init__(self, id=None, packet=None):
		"""\
		SQLObject(id)
		SQLObject(packet)
		SQLObject()

		Create an object from the database using id.
		Create an object from a network packet.
		Create an empty object.
		"""
		self.tablename = self.tablename
		
		if id != None:
			self.load(id)
		if packet != None:
			self.from_packet(packet)

	def todict(self):
		return self.__dict__

	def load(self, id):
		"""\
		load(id)

		Loads a thing from the database.
		"""
		self.id = id
		
		result = db.query("""SELECT * FROM %(tablename)s WHERE id=%(id)s""", self.todict())
		if len(result) != 1:
			raise NoSuch("%s does not exists" % id)

		self.__dict__.update(result[0])

	def save(self):
		"""\
		save()

		Saves a thing to the database.
		"""
		# Build SQL query, there must be a better way to do this...
		if hasattr(self, 'id') and self.id == 0:
			SQL = """UPDATE %(tablename)s SET """
		else:
			SQL = """REPLACE %(tablename)s SET """

		for finfo in self.description:
			if finfo['Field'] == 'id' and not hasattr(self, 'id'):
				continue
			
			SQL += """`%(Field)s` = "%%(%(Field)s)s", """ % finfo
		SQL = SQL[:-2]

		db.query(SQL, self.todict())

		if not hasattr(self, 'id'):
			self.id = db.connection.insert_id()

	def remove(self):
		"""\
		remove()

		Removes an object from the database.
		"""
		# Remove the common attribute
		db.query("""DELETE FROM %(tablename)s WHERE id=%(id)s""", self.todict())

	def insert(self):
		"""\
		insert()

		Inserts an object into the database.
		"""
		self.save()

	def to_packet(self, sequence):
		"""\
		to_packet(sequence) -> netlib.Packet

		Returns a Thousand Parsec network packet using the sequence number.
		"""
		pass

	def from_packet(self, packet):
		"""\
		from_packet(packet)

		Makes an object out of a Thousand Parsec packet.
		"""
		self.__dict__.update(packet.__dict__)

	
class SQLWithAttrBase(SQLBase):
	def attributes(self):
		"""\
		*Internal*

		Get a list of attributes this object type has.
		"""
		if not hasattr(self, "_attributes"):
			self._attributes = db.query("""SELECT * FROM %(tablename)s_type_attr WHERE %(fieldname)s_type_id=%(type)s ORDER BY id""", self.todict())
		return self._attributes
	attributes = property(attributes)

	def __init__(self, id=None, packet=None, type=None):
		self.fieldname = self.fieldname

		if id == None and packet == None and type == None:
			raise ValueError("Can not create an object without type.")

		if type != None:
			self.type = type
			self.defaults()

		SQLBase.__init__(self, id, packet)

	def defaults(self):
		"""\
		Sets all the attributes to there default values.
		"""
		# Set the default attributes
		for attribute in self.attributes:
			if not hasattr(self, attribute['name']):
				setattr(self, attribute['name'], pickle.loads(attribute['default']))

	def load(self, id):
		"""\
		load(id)

		Loads a thing from the database.
		"""
		SQLBase.load(self, id)

		self.defaults()

		# Now for the type specific attributes
		for attribute in self.attributes:
			value = db.query("""SELECT value FROM %(tablename)s_attr WHERE %(fieldname)s_id=%(id)s AND %(fieldname)s_type_attr_id=%(aid)s""", self.todict(), aid=attribute['id'])
			setattr(self, attribute['name'], pickle.loads(value[0]['value']))

	def save(self):
		"""\
		save()

		Saves a thing to the database.
		"""
		SQLBase.save(self)

		# Now for the type specific attributes
		for attribute in self.attributes:
			value = pickle.dumps(getattr(self, attribute['name']))
			db.query("""REPLACE %(tablename)s_attr VALUES (%(id)s, %(aid)s, "%(value)s")""", self.todict(), aid=attribute['id'], value=value)

	def remove(self):
		"""\
		remove()

		Removes an object from the database.
		"""
		# Remove the common attribute
		SQLBase.remove(self)

		db.query("""DELETE FROM %(tablename)s_attr WHERE %(fieldname)s_id=%(id)s""", self.todict())

	def from_packet(self, packet):
		"""\
		from_packet(packet)

		Makes an object out of a Thousand Parsec packet.
		"""
		self.type = packet.type

		self.defaults()
		
		SQLBase.from_packet(self, packet)
		
