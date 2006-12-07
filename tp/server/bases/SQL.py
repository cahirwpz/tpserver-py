"""\
Database backed bases for the objects.
"""
# Module imports
from sqlalchemy import *

try:
	import cPickle as pickle
except ImportError:
	import pickle
import copy
import time

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
		t = self.table
		result = t.select(order_by=[desc(t.c.time)], limit=1).execute().fetchall()
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
		
		t = self.table
		result = t.select([t.c.id, t.c.time], order_by=[desc(t.c.time)], limit=amount, offset=start).execute().fetchall()
		return [(x['id'], x['time']) for x in result]
	ids = classmethod(ids)

	def amount(cls, user):
		"""\
		amount(user) -> int

		Get the number of records in this table (that the user can see).
		"""
		result = self.table.select([func.count(self.table.c.time)]).execute().fetchall()
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
		
		result = self.table.select(self.table.c.id==id).execute().fetchall()
		if len(result) != 1:
			raise NoSuch("%s does not exists" % id)

		self.__dict__.update(result[0])
		# FIXME: HACK!
		for name in self.__dict__:
			value = self.__dict__[name]
			if type(value) is buffer:
				self.__dict__[name] = str(value)

	def save(self):
		"""\
		save()

		Saves a thing to the database.
		"""
		self.time = time.time()
		
		# Build SQL query, there must be a better way to do this...
		if hasattr(self, 'id'):
			method = 'replace'
		else:
			method = 'insert'

		# FIXME: This is MySQL specific....
		arguments = {}
		for column in self.table.columns:
			if c.name == 'id' and not hasattr(self, 'id'):
				continue
			if hasattr(self, column.name):
				arguments[column.name] = getattr(self, column.name)
			
		result = getattr(self.table, method).execute(arguments)
		print result

		if not hasattr(self, 'id'):
			self.id = db.connection.insert_id()
			print "Newly inserted id is", self.id

	def remove(self):
		"""\
		remove()

		Removes an object from the database.
		"""
		# Remove the common attribute
		self.table.delete(self.table.c.id==self.id).execute()

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

def SQLTypedTable(name):
	t = Table(name+"_extra",
		Column(name,	Integer,	 default=0,  nullable = False, index=True, primary_key=True),
		Column('name',	String(255), default='', nullable = False, index=True, primary_key=True),
		Column('key',	String(255), default='', nullable = False, index=True, primary_key=True),
		Column('value',	Binary),
#		Column('time',	DateTime,    nullable=False, index=True, onupdate=func.current_timestamp()),

		# Extra properties
		ForeignKeyConstraint([name], [name+'.id']),
	)
	# Index on the ID and name
	Index('idx_'+name+'xtr_idname', getattr(t.c, name), t.c.name)
	Index('idx_'+name+'xtr_idnamevalue', getattr(t.c, name), t.c.name, t.c.value)

	return t

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
			self._default = default
			self.level = level
			self.type = type
			self.desc = desc

		def get_default(self):
			return copy.deepcopy(self._default)
		default = property(get_default)

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
		te = self.table_extra
		SQLBase.load(self, id)
			
		self.__upgrade__(self.type)

		# Load the extra properties from the object_extra table
		results = te.select(te.c.object==self.id).execute().fetchall()
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

	def save(self, preserve=True):
		"""\
		save()

		Saves a thing to the database.
		"""
#		db.begin()

		te = self.table_extra
		try:
			SQLBase.save(self)

			for attribute in self.attributes.values():
				if type(attribute.default) is types.DictType:
					te.delete(te.c.object==self.id, te.c.name==attribute.name).execute()
					for key, value in getattr(self, attribute.name).items():
						if not isSimpleType(key):
							raise ValueError("The key %s in dictionary attribute %s is not a simple type." %  (value, key, attribute.name))
						else:
							key = repr(key)
						
						if not isSimpleType(value):
							raise ValueError("The value %s with key %s in dictionary attribute %s is not a simple type." %  (value, key, attribute.name))
						else:
							value = repr(value)
						
						te.insert().execute(object=self.id, name=attribute.name, key=key, value=value)
				else:
					if isSimpleType(attribute.default):
						value = repr(getattr(self, attribute.name))
					else:
						value = pickle.dumps(getattr(self, attribute.name))
					te.replace().execute(object=self.id, name=attribute.name, key='', value=value)
		except Exception, e:
#			db.rollback()
			raise
		else:
#			db.commit()
			pass

	def remove(self):
		"""\
		remove()

		Removes an object from the database.
		"""
#		db.begin()
		try:
			self.table_extra.delete().execute(id=self.id)
			SQLBase.remove(self)
		except Exception, e:
#			db.rollback()
			raise
		else:
#			db.commit()
			pass

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

