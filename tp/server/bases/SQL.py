"""\
Database backed bases for the objects.
"""
# Module imports
from sqlalchemy import *
from tp.server.db import *

try:
	import cPickle as pickle
except ImportError:
	import pickle
import copy
import time
from array import array

# These types go through repr fine
import types
types.SimpleTypes = [types.BooleanType, types.ComplexType, types.FloatType, 
					 types.IntType, types.LongType, types.NoneType]+list(types.StringTypes)
types.SimpleCompoundTypes = [types.ListType, types.TupleType]

def isSimpleType(value):
	if type(value) in types.SimpleTypes:
		return True
	
	elif type(value) in types.SimpleCompoundTypes:
		for subvalue in value:
			if not isSimpleType(subvalue):
				return False
		return True
		
	else:
		return False

def quickimport(s):
	return getattr(__import__(s, globals(), locals(), s.split(".")[-1]), s.split(".")[-1])

class NoSuch(Exception):
	pass

class PermissionDenied(Exception):
	pass

class SQLBase(object):
	"""\
	A class which stores it's data in a SQL database.
	"""
	def modified(cls, user):
		"""\
		modified(user) -> unixtime
		
		Gets the last modified time for the type.
		"""
		# FIXME: This gives the last modified for anyone time, not for the specific user.
		t = cls.table
		result = select([t], order_by=[desc(t.c.time)], limit=1).execute().fetchall()
		if len(result) == 0:
			return 0
		return result[0]['time']
	modified = classmethod(modified)

	def ids(cls, user=None, start=0, amount=-1):
		"""\
		ids([user, start, amount]) -> [id, ...]
		
		Get the last ids for this (that the user can see).
		"""
		t = cls.table
		if amount == -1:
			result = select([t.c.id, t.c.time], order_by=[desc(t.c.time)], offset=start).execute().fetchall()
		else:
			result = select([t.c.id, t.c.time], order_by=[desc(t.c.time)], offset=start, limit=amount).execute().fetchall()
		return [(x['id'], x['time']) for x in result]
	ids = classmethod(ids)

	def amount(cls, user):
		"""\
		amount(user) -> int

		Get the number of records in this table (that the user can see).
		"""
		result = select([func.count(cls.table.c.time).label('count')]).execute().fetchall()
		if len(result) == 0:
			return 0
		return result[0]['count']
	amount = classmethod(amount)

	def realid(cls, user, id):
		"""\
		realid(user, id) -> id
		
		Get the real id for an object (from id the user sees).
		"""
		return id
	realid = classmethod(realid)

	def __init__(self, id=None):
		"""\
		SQLObject(id)
		SQLObject(packet)
		SQLObject()

		Create an object from the database using id.
		Create an object from a network packet.
		Create an empty object.
		"""
		if not (id is None):
			self.load(id)

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
		
		result = select([self.table], self.table.c.id==id).execute().fetchall()
		if len(result) != 1:
			raise NoSuch("%s does not exists" % id)

		for key, value in result[0].items():
			if isinstance(value, buffer):
				value = str(value)
			elif isinstance(value, array):
				value = value.tostring()

			setattr(self, key, value)

	def save(self, forceinsert=False):
		"""\
		save()

		Saves a thing to the database.
		"""
		if hasattr(self, 'time'):
			del self.time

		# Build SQL query, there must be a better way to do this...
		if forceinsert or not hasattr(self, 'id'):
			method = insert(self.table)
		else:
			method = update(self.table, self.table.c.id==self.id)

		arguments = {}
		for column in self.table.columns:
			if column.name == 'id' and not hasattr(self, 'id'):
				continue
			if hasattr(self, column.name):
				arguments[column.name] = getattr(self, column.name)
		
		result = method.execute(**arguments)

		if not hasattr(self, 'id'):
			self.id = result.last_inserted_ids()[0]
			if default_metadata.engine.echo:
				print "Newly inserted id is", self.id

	def remove(self):
		"""\
		remove()

		Removes an object from the database.
		"""
		# Remove the common attribute
		delete(self.table, self.table.c.id==self.id).execute()

	def insert(self):
		"""\
		insert()

		Inserts an object into the database.
		"""
		self.save(forceinsert=True)

	def to_packet(self, user, sequence):
		"""\
		to_packet(user, sequence) -> netlib.Packet

		Returns a Thousand Parsec network packet using the sequence number.
		"""
		# FIXME: There is a possibility that this leaks information...
		if not self.allowed(user):
			raise PermissionDenied("You are not allowed to access that.")
		return self.protect(user)

	def from_packet(cls, user, packet):
		"""\
		from_packet(game, packet)

		Makes an server object out of a Thousand Parsec packet.
		"""
		# Create an empty object
		self = cls()

		# Populate it with values from the packet
		for key, value in packet.__dict__.items():
			# Ignore special attributes
			if key.startswith("_"):
				continue

			setattr(self, key, value)

		# Return the newly created object
		return self
	from_packet = staticmethod(from_packet)

	def allowed(self, user):
		"""\
		allowed(user) -> boolean

		Returns a boolean which tells if a user can even see this object.
		"""
		return True

	def protect(self, user):
		"""\
		protect(user) -> object

		Returns a version of this object which shows only details which the user is 
		allowed to see.
		"""
		return copy.deepcopy(self)

def SQLTypedTable(name):
	t = Table(name+"_extra",
		Column('game',	Integer,	 nullable=False, index=True),
		Column('oid',	Integer,	 nullable=False, index=True, primary_key=True),
		Column('name',	String(255), default='', nullable=False, index=True, primary_key=True),
		Column('key',	String(255), default='', nullable=False, index=True, primary_key=True, quote=True),
		Column('value',	Binary),
		Column('time',	DateTime, nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		# Extra properties
		ForeignKeyConstraint(['oid'],  [name+'.id']),
		ForeignKeyConstraint(['game'], ['game.id']),
	)
	# Index on the ID and name
	Index('idx_'+name+'xtr_idname', t.c.oid, t.c.name)
	Index('idx_'+name+'xtr_idnamevalue', t.c.oid, t.c.name, t.c.key)

	t._name = name

	return t

_marker = []
class SQLTypedBase(SQLBase):
	"""\
	A class which stores it's data in a SQL database.
	It also has a subclass associated with it which stores extra data.
	"""
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
			self._default = default
			self.level = level
			self.type = type
			self.desc = desc

		def get_default(self):
			return copy.deepcopy(self._default)
		default = property(get_default)

	def type_get(self):
		return self.__class__.__module__
	def type_set(self, type):
#		if self.__class__ != SQLTypedBase:
#			raise TypeError('Can not set the type a second time!')
		self.__class__ = quickimport(type)		
		self.__upgrade__()

	type = property(type_get, type_set)

	def __init__(self, id=None, type=None):
		if id != None:
			SQLBase.__init__(self, id)
		if type != None:
			self.type = type
		self.defaults()

	def __upgrade__(self):
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
		te = self.table_extra
		SQLBase.load(self, id)
			
		# Load the extra properties from the object_extra table
		results = select([te], te.c.oid==self.id).execute().fetchall()
		if len(results) > 0:
			for result in results:
				name, key, value = result['name'], result['key'], result['value']

				if not self.attributes.has_key(name):
					continue
				attribute = self.attributes[name]
				
				if type(attribute.default) is types.DictType:
					if not hasattr(self, name):
						setattr(self, name, {})

					getattr(self, name)[eval(key)] = eval(str(value))
					continue
			
				elif isSimpleType(attribute.default):
					value = eval(str(value))
				else:
					value = pickle.loads(value)
					
				setattr(self, name, value)

	def save(self, preserve=True, forceinsert=False):
		"""\
		save()

		Saves a thing to the database.
		"""
		trans = dbconn.begin()

		te = self.table_extra
		try:
			SQLBase.save(self, forceinsert)

			for attribute in self.attributes.values():
				if type(attribute.default) is types.DictType:
					delete(te, (te.c.oid==self.id) & (te.c.name==attribute.name)).execute()
					for key, value in getattr(self, attribute.name).items():
						if not isSimpleType(key):
							raise ValueError("The key %s in dictionary attribute %s is not a simple type." %  (value, key, attribute.name))
						else:
							key = repr(key)
						
						if not isSimpleType(value):
							raise ValueError("The value %s with key %s in dictionary attribute %s is not a simple type." %  (value, key, attribute.name))
						else:
							value = repr(value)
						
						insert(te).execute(oid=self.id, name=attribute.name, key=key, value=value)
				else:
					if isSimpleType(attribute.default):
						value = repr(getattr(self, attribute.name))
					else:
						value = pickle.dumps(getattr(self, attribute.name))
					# Check if attribute exists
					result = select([te], (te.c.oid==self.id) & (te.c.name==attribute.name) & (te.c.key=='')).execute().fetchall()
					if len(result) > 0:
						update(te, (te.c.oid==self.id) & (te.c.name==attribute.name) & (te.c.key=='')).execute(oid=self.id, name=attribute.name, key='', value=value)
					else:
						insert(te).execute(oid=self.id, name=attribute.name, key='', value=value)
		except Exception, e:
			trans.rollback()
			raise
		else:
			trans.commit()
			pass

	def remove(self):
		"""\
		remove()

		Removes an object from the database.
		"""
		trans = dbconn.begin()
		try:
			delete(self.table_extra).execute(id=self.id)
			SQLBase.remove(self)
		except Exception, e:
			trans.rollback()
			raise
		else:
			trans.commit()
			pass

	def from_packet(cls, user, packet):
		"""\
		from_packet(packet)

		Makes an object out of a Thousand Parsec packet.
		"""
		# Get the mapping
		map = getattr(user.playing.ruleset, cls.__name__.lower() + 'map')
		
		# Create an instance of this object
		self = map[packet.type]()

		# FIXME: This is probably bad...
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
		return self
	from_packet = staticmethod(from_packet)

	def to_packet(self, user, sequence, args):
		for attribute in self.attributes.values():
			if attribute.level == "public":
				value = getattr(self, attribute.name)
			elif attribute.level == "protected":
				value = getattr(self, "fn_"+attribute.name)()
			else:
				continue
			args.append(value)

