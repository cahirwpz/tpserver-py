
try:
	import cPickle as pickle
except ImportError:
	import pickle
import copy
import time

from config import db

def quickimport(s):
	return getattr(__import__(s, globals(), locals(), s.split(".")[-1]), s.split(".")[-1])

class NoSuch(Exception):
	pass

class SQLBase(object):
	"""\
	A class which stores it's data in a SQL database.
	"""
	def _description(cls):
		"""\
		*Internal*

		Get a description of the object.
		"""
		if not hasattr(cls, "__description"):
			cls.__description = db.query("DESCRIBE %(tablename)s", tablename=cls.tablename)
		return cls.__description
	_description = classmethod(_description)
	description = property(_description)

	def modified(cls):
		"""\
		Gets the last modified time for the whole table.
		"""
		result = db.query("SELECT time FROM %(tablename)s ORDER BY time DESC LIMIT 1", tablename=cls.tablename)
		return result[0]['time']
	modified = classmethod(modified)

	def ids(cls, start, amount):
		"""\
		Get the last ids for this.
		"""
		if amount == -1:
			amount = 2**64
		
		result = db.query("SELECT id, time FROM %(tablename)s LIMIT %(amount)s OFFSET %(start)s", tablename=cls.tablename, start=start, amount=amount)
		return [(x['id'], x['time']) for x in result] 
#		if "ids" in cls._description():
#			if "time" in cls._description():
#				result = db.query("SELECT id, time FROM %(tablename)s LIMIT %(length)i OFFSET %(start)i ", tablename=cls.tablename, start=start, length=length)
#			else:
#				result = db.query("SELECT id FROM %(tablename)s LIMIT %(length)i OFFSET %(start)i", tablename=cls.tablename, start=start, length=length)
#			return [(x['id'], x['time']) for x in result] 
#		raise ValueError("Can not use this method for this table.")
	ids = classmethod(ids)

	def amount(cls):
		"""\
		Get the number of records in this table.
		"""
		return db.query("SELECT count(*) FROM %(tablename)s", tablename=cls.tablename)[0]['count(*)']
	amount = classmethod(amount)

	def realid(cls, id, pid):
		"""\
		Get the real id for an object.
		"""
		return id
	realid = classmethod(realid)

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
		"""\
		todict()

		Turns this object into a dictionary.
		"""
		return copy.copy(self.__dict__)

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
		self.time = time.time()
		
		# Build SQL query, there must be a better way to do this...
		if hasattr(self, 'id') and self.id == 0:
			SQL = """UPDATE %(tablename)s SET """
		else:
			SQL = """REPLACE %(tablename)s SET """

		# FIXME: This is MySQL specific....
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
		if hasattr(self, "id"):
			del self.id
		self.save()

	def to_packet(self, sequence):
		"""\
		to_packet(sequence) -> netlib.Packet

		Returns a Thousand Parsec network packet using the sequence number.
		"""
		raise NotImplimented("This method has not been implimented.")

	def from_packet(self, packet):
		"""\
		from_packet(packet)

		Makes an object out of a Thousand Parsec packet.
		"""
		for key, value in packet.__dict__.items():
			# Ignore special attributes
			if key.startswith("_"):
				continue

			setattr(self, key, value)

	def allowed(self, user):
		"""\
		allowed(user)

		User is allowed to access this object.
		"""
		return True

	def __repr__(self):
		return self.__str__()

_marker = []
class SQLTypedBase(SQLBase):
	"""\
	A class which stores it's data in a SQL database.
	It also has a subclass associated with it which stores extra data.
	"""
	types = {}

	attributes = {}
	attributes__doc__ = """\
Extra attributes this type defines.

{"<name>": Attribute(<name>, <default>, <level>)}
"""
	class Attribute:
		def __init__(self, name, default, level, type=-1, desc=""):
			if level not in ('public', 'protected', 'private'):
				raise ValueError("Invalid access level for attribute.")

			self.name = name
			self.default = default
			self.level = level
			self.type = type
			self.desc = desc

	
	def __init__(self, id=None, packet=None, type=None, typeno=None):
		if hasattr(self, "typeno"):
			typeno = self.typeno
	
		if id == None and packet == None and type == None and typeno == None:
			raise ValueError("Can not create an object without type.")

		SQLBase.__init__(self, id, packet)

		self.__upgrade__(type, typeno)

	def __upgrade__(self, type=None, typeno=None):
		if typeno != None:
			type = self.types[typeno].__module__

		if type != None:
			self.type = type

			self.__class__ = quickimport(self.type)
		
		self.defaults()

	def __getattr__(self, key, default=_marker):
		if hasattr(self, 'extra') and self.extra.has_key(key):
			# Return the extra value
			return self.extra[key]
		elif self.attributes.has_key(key):
			# Return the default
			return self.attributes[key].default
		elif not default is _marker:
			return default
		raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, key))

	def __setattr__(self, key, value):
		if self.attributes.has_key(key):
			try:
				self.extra[key] = value
			except AttributeError:
				self.extra = {}
				self.extra[key] = value
		else:
			SQLBase.__setattr__(self, key, value)

	def defaults(self):
		"""\
		Sets all the attributes to there default values.
		"""
		# Set the default attributes
		if not hasattr(self, "extra"):
			self.extra = {}
		
		for attribute in self.attributes.values():
			if not hasattr(self, attribute.name):
				setattr(self, attribute.name, attribute.default)

	def load(self, id):
		"""\
		load(id)

		Loads a thing from the database.
		"""
		SQLBase.load(self, id)
		self.extra = pickle.loads(self.extra)

		self.__upgrade__(self.type)

	def save(self, preserve=True):
		"""\
		save()

		Saves a thing to the database.
		"""
		self.extra = pickle.dumps(self.extra)
		SQLBase.save(self)
		if preserve:
			self.extra = pickle.loads(self.extra)

	def from_packet(self, packet):
		"""\
		from_packet(packet)

		Makes an object out of a Thousand Parsec packet.
		"""
		self.__upgrade__(typeno=packet.type)

		for key, value in packet.__dict__.items():
		
			# Ignore special attributes
			if key.startswith("_") or key == "extra" or key == "type":
				continue

			if self.attributes.has_key(key):
				if self.attributes[key].level == 'public':
					setattr(self, key, value)
				elif self.attributes[key].level == 'protected':
					getattr(self, "fn_"+key)(value)
			else:
				setattr(self, key, value)

	def to_packet(self, sequence, args):
		"""\
		to_packet(packet)

		"""
		for attribute in self.attributes.values():
			if attribute.level == "public":
				value = getattr(self, attribute.name)
			elif attribute.level == "protected":
				value = getattr(self, "fn_"+attribute.name)()
			else:
				continue
			args.append(value)

