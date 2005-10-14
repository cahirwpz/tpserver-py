
try:
	import cPickle as pickle
except ImportError:
	import pickle
import copy
import time

from config import db

import types
# These types go through repr fine
types.SimpleTypes = [types.BooleanType, types.ComplexType, types.FloatType, 
					 types.IntType, types.LongType, types.NoneType]+list(types.StringTypes)

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

	def modified(cls, user):
		"""\
		modified(user) -> unixtime
		
		Gets the last modified time for the type.
		"""
		# FIXME: This gives the last modified for anyone time, not for the specific user.
		result = db.query("SELECT time FROM %(tablename)s ORDER BY time DESC LIMIT 1", tablename=cls.tablename)
		if len(result) == 0:
			return 0
		return result[0]['time']
	modified = classmethod(modified)

	def ids(cls, user, start, amount):
		"""\
		ids(user, start, amount) -> [id, ...]
		
		Get the last ids for this (that the user can see).
		"""
		if amount == -1:
			amount = 2**64
		
		result = db.query("SELECT id, time FROM %(tablename)s ORDER BY time DESC LIMIT %(amount)s OFFSET %(start)s", tablename=cls.tablename, start=start, amount=amount)
		return [(x['id'], x['time']) for x in result] 
		
#		if "ids" in cls._description():
#			if "time" in cls._description():
#				result = db.query("SELECT id, time FROM %(tablename)s LIMIT %(length)i OFFSET %(start)i ", tablename=cls.tablename, start=start, length=length)
#			else:
#				result = db.query("SELECT id FROM %(tablename)s LIMIT %(length)i OFFSET %(start)i", tablename=cls.tablename, start=start, length=length)
#			return [(x['id'], x['time']) for x in result] 
#		raise ValueError("Can not use this method for this table.")
	ids = classmethod(ids)

	def amount(cls, user):
		"""\
		amount(user) -> int

		Get the number of records in this table (that the user can see).
		"""
		result = db.query("SELECT count(*) FROM %(tablename)s", tablename=cls.tablename)
		if len(result) == 0:
			return 0
		return result[0]['count(*)']
	amount = classmethod(amount)

	def realid(cls, user, id):
		"""\
		realid(user, id) -> id
		
		Get the real id for an object (from id the user sees).
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
		todict() -> dict

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
		for finfo in self._description():
			if finfo['Field'] == 'id' and not hasattr(self, 'id'):
				continue
			
			SQL += """`%(Field)s` = '%%(%(Field)s)s', """ % finfo
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
		allowed(user) -> boolean

		Returns a boolean which tells if a user can even see this object.
		"""
		return copy.deepcopy(self)


	def protect(self, user):
		"""\
		protect(user) -> object

		Returns a version of this object which shows only details which the user is 
		allowed to see.
		"""
		return copy.deepcopy(self)

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

	def defaults(self):
		"""\
		Sets all the attributes to their default values.
		"""
		for attribute in self.attributes.values():
			if not hasattr(self, attribute.name):
				setattr(self, attribute.name, attribute.default)

	def load(self, id):
		"""\
		load(id)

		Loads a thing from the database.
		"""
		SQLBase.load(self, id)
			
		self.__upgrade__(self.type)

		# Load the extra properties from the object_extra table
		results = db.query("""SELECT name, `key`, value FROM %(tablename_extra)s WHERE %(tablename)s=%(id)s""", 
			tablename_extra=self.tablename_extra, tablename=self.tablename, id=self.id)
		if len(results) > 0:
			for result in results:
				print result
				name, key, value = result['name'], result['key'], result['value']
				attribute = self.attributes[name]
				
				if type(attribute.default) is types.DictType:
					if not hasattr(self, name):
						setattr(self, name, {})

					getattr(self, name)[key] = value
					continue
			
				elif type(attribute.default) in types.SimpleTypes:
					value = eval(value)
				else:
					value = pickle.loads(value)
					
				setattr(self, name, value)

	def save(self, preserve=True):
		"""\
		save()

		Saves a thing to the database.
		"""
		db.begin()
		try:
			SQLBase.save(self)

			for attribute in self.attributes.values():
				if type(attribute.default) is types.DictType:
					print attribute.name, getattr(self, attribute.name).items()
					for key, value in getattr(self, attribute.name).items():
						if type(attribute.default) in types.SimpleTypes:
							value = repr(getattr(self, attribute.name))
						else:
							value = pickle.dumps(getattr(self, attribute.name))
						
						print "self.id -->", repr(self.id)
						print "key   ---->", repr(key)
						print "value ---->", repr(value)
						db.query("REPLACE INTO %(tablename_extra)s SET %(tablename)s=%(id)s, name='%(name)s', `key`=%(key)s, value='%(value)s'",
							tablename_extra=self.tablename_extra, tablename=self.tablename, id=self.id, name=attribute.name, key=key, value=value)
				else:
					if type(attribute.default) in types.SimpleTypes:
						value = repr(getattr(self, attribute.name))
					else:
						value = pickle.dumps(getattr(self, attribute.name))
					db.query("REPLACE INTO %(tablename_extra)s SET %(tablename)s=%(id)s, name='%(name)s', `key`='', value='%(value)s'",
						tablename_extra=self.tablename_extra, tablename=self.tablename, id=self.id, name=attribute.name, value=value)
		
		except Exception, e:
			db.rollback()
			raise
		else:
			db.commit()

	def remove(self):
		"""\
		remove()

		Removes an object from the database.
		"""
		db.begin()
		try:
			db.query("DELETE FROM %(tablename_extra)s WHERE %(tablename)s=%(id)s", 
				tablename_extra=self.tablename_extra, tablename=self.tablename, id=self.id)
			SQLBase.remove(self)
		except Exception, e:
			db.rollback()
			raise
		else:
			db.commit()

	def from_packet(self, packet):
		"""\
		from_packet(packet)

		Makes an object out of a Thousand Parsec packet.
		"""
		self.__upgrade__(typeno=packet.type)

		for key, value in packet.__dict__.items():
		
			# Ignore special attributes
			if key.startswith("_") or key == "type":
				continue

			if self.attributes.has_key(key):
				if self.attributes[key].level == 'public':
					setattr(self, key, value)
				elif self.attributes[key].level == 'protected':
					getattr(self, "fn_"+key)(value)
			else:
				setattr(self, key, value)

	def to_packet(self, sequence, args):
		for attribute in self.attributes.values():
			if attribute.level == "public":
				value = getattr(self, attribute.name)
			elif attribute.level == "protected":
				value = getattr(self, "fn_"+attribute.name)()
			else:
				continue
			args.append(value)

