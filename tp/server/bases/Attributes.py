#!/usr/bin/env python

import copy

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

# from tp.server.db import DatabaseManager
from tp.server.db.enum import Enum

from SQL import SQLBase

class AttributeSet( SQLBase ):
	@classmethod
	def InitMapper( cls, metadata, Object ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',      Integer, index = True, primary_key = True ),
				Column('name',    String(255), nullable = False, index = True),
				Column('type',    Text),
				Column('access',  Enum( cls.AccessType ), nullable = False ),
				Column('default', Binary, nullable = True ),
				Column('mtime',   DateTime,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		mapper( cls, cls.__table__ )

class AttributeType( SQLBase ):
	AccessType  = [ 'public', 'protected', 'private' ]

	@classmethod
	def InitMapper( cls, metadata, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',      Integer, index = True, primary_key = True ),
				Column('name',    String(255), nullable = False, index = True ),
				Column('type',    Text, nullable = False ),
				Column('access',  Enum( cls.AccessType ), nullable = False ),
				Column('default', Binary, nullable = True ))

		mapper( cls, cls.__table__ )

class Attribute_( SQLBase ):
	@classmethod
	def InitMapper( cls, metadata, Order ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',       Integer, index = True, primary_key = True ),
				Column('name',     String( 255 ), index = True, nullable = False ),   
				Column('order_id', ForeignKey( Order.id ), nullable = False, index = True ),
				Column('value_id', ForeignKey( AttributeValue.id ), nullable = False ),
				Column('type_id',  ForeignKey( AttributeType.id ), nullable = False ),
				UniqueConstraint( 'order_id', 'value_id', 'type_id' ))

		mapper( cls, cls.__table__ )
	
class Attribute( object ):
	def __init__( self, type, level, default = None, description = None ):
		self.type			= type
		self.level			= level
		self.default		= default
		self.description	= description

class SQLTypedBase(SQLBase):#{{{
	"""
	A class which stores it's data in a SQL database.
	It also has a subclass associated with it which stores extra data.
	"""
	attributes = {}
	attributes__doc__ = """\
Extra attributes this type defines.

{"<name>": Attribute(<name>, <default>, <level>)}
"""
	@property
	def type(self):
		return self.__class__.__module__

	@type.setter
	def type(self, type):
#		if self.__class__ != SQLTypedBase:
#			raise TypeError('Can not set the type a second time!')
		self.__class__ = quickimport(type)		
		self.__upgrade__()

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
		results = select([te], te.c.oid==self.id, order_by=[te.c.name, te.c.key]).execute().fetchall()
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
			
				elif type(attribute.default) is types.ListType:
					if not hasattr(self, name):
						setattr(self, name, [])

					if len(getattr(self, name)) != eval(key):
						raise TypeError('Some how you managed to get a list which is missing an element!')

					getattr(self, name).append(eval(str(value)))
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
				if type(attribute.default) in (types.DictType, types.ListType):
					delete(te, (te.c.oid==self.id) & (te.c.name==attribute.name)).execute()

					if type(attribute.default) is types.ListType:
						items = enumerate(getattr(self, attribute.name))
					else:
						items = getattr(self, attribute.name).iteritems()

					for key, value in items:
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
			
			trans.commit()
		except Exception, e:
			trans.rollback()
			raise

	def remove(self):
		"""\
		remove()

		Removes an object from the database.
		"""
		trans = dbconn.begin()
		try:
			t = self.table_extra
			delete(t, t.c.oid==bindparam('id')).execute(id=self.id)
			SQLBase.remove(self)

			trans.commit()
		except Exception, e:
			trans.rollback()
			raise

	@staticmethod
	def from_packet(cls, user, packet):
		"""\
		from_packet(packet)

		Makes an object out of a Thousand Parsec packet.
		"""
		# Get the mapping
		map = getattr(user.playing.ruleset, cls.__name__.lower() + 'map')
		
		# Create an instance of this object
		self = map[packet._subtype]()

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
				if hasattr(self, key):
					print "Ekk! Tried to set %s but it already existed (%s)" % (key, getattr(self, key))
					continue

				setattr(self, key, value)
		return self

	def to_packet(self, user, sequence):
		self = SQLBase.to_packet(self, user, sequence)

		args = []
		for attribute in self.attributes.values():
			if attribute.level == "public":
				value = getattr(self, attribute.name)
			elif attribute.level == "protected":
				value = getattr(self, "fn_"+attribute.name)()
			else:
				continue
			args.append(value)
		return self, args
#}}}

__all__ = [ 'Attribute' ]
