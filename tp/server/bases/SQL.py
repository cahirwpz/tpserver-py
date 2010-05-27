"""
Database backed bases for the objects.
"""

from sqlalchemy import *
from tp.server.db import *

import copy
from datetime import datetime
from array import array

class NoSuchThing( Exception ):#{{{
	pass
#}}}

class PermissionDenied( Exception ):#{{{
	pass
#}}}

class SQLUtils( object ):#{{{
	def __get__( self, owner, cls):
		self.cls = cls
		return self

	def modified(self, user):
		"""
		modified(user) -> unixtime
		
		Gets the last modified time for the type.
		"""
		t = self.cls.table
		# FIXME: This gives the last modified for anyone time, not for the specific user.
		result = select([t], order_by=[desc(t.c.time)], limit=1).execute().fetchall()
		if len(result) == 0:
			return datetime.fromtimestamp(0)
		return result[0]['time']

	def ids(self, user=None, start=0, amount=-1):
		"""
		ids([user, start, amount]) -> [id, ...]
		
		Get the last ids for this (that the user can see).
		"""
		t = self.cls.table

		if amount == -1:
			result = select([t.c.id, t.c.time], order_by=[desc(t.c.time)], offset=start).execute().fetchall()
		else:
			result = select([t.c.id, t.c.time], order_by=[desc(t.c.time)], offset=start, limit=amount).execute().fetchall()
		return [(x['id'], x['time']) for x in result]

	def amount(self, user=None):
		"""
		amount(user) -> int

		Get the number of records in this table (that the user can see).
		"""
		t = self.cls.table

		result = select([func.count(t.c.time).label('count')]).execute().fetchall()

		if len(result) == 0:
			return 0
		else:
			return result[0]['count']

	def realid(self, user, id):
		"""
		realid(user, id) -> id
		
		Get the real id for an object (from id the user sees).
		"""
		return id
#}}}

class SQLBase( object ):#{{{
	Utils = SQLUtils()

	"""
	A class which stores it's data in a SQL database.
	"""
	def __init__(self, id=None):
		"""
		SQLObject(id)
		SQLObject()

		Create an object from the database using id.
		Create an empty object.
		"""
		if id is not None:
			self.load(id)

	def load(self, id):
		"""
		load(id)

		Loads a thing from the database.
		"""
		self.id = id
		
		result = select([self.table], self.table.c.id==id).execute().fetchall()
		if len(result) != 1:
			raise NoSuchThing("%s does not exists" % id)

		for key, value in result[0].items():
			if isinstance(value, buffer):
				value = str(value)
			elif isinstance(value, array):
				value = value.tostring()

			setattr(self, key, value)

	def save(self, forceinsert=False):
		"""
		save()

		Saves a thing to the database.
		"""
		if hasattr(self, 'time'):
			del self.time

		trans = dbconn.begin()
		try:
			arguments = {}

			# Build SQL query, there must be a better way to do this...
			if forceinsert or not hasattr(self, 'id'):
				method = insert(self.table)
	
				# FIXME: This is bad!
				id = select([func.max(self.table.c.id+1)], limit=1).execute().fetchall()[0][0]
				if id is None:
					id = 1
				arguments['id'] = id
			else:
				method = update(self.table, self.table.c.id==self.id)

			for column in self.table.columns:
				if column.name == 'id' and not hasattr(self, 'id'):
					continue
				if hasattr(self, column.name):
					arguments[column.name] = getattr(self, column.name)
			
			result = method.execute(**arguments)

			if not hasattr(self, 'id'):
				self.id = id
				if metadata.bind.echo:
					print "Newly inserted id is", self.id

			if not hasattr(self, 'game'):
				if dbconn.game != None:
					self.game = dbconn.game

			trans.commit()
		except:
			trans.rollback()
			raise

	def remove(self):
		"""
		remove()

		Removes an object from the database.
		"""
		# Remove the common attribute
		delete(self.table, self.table.c.id==bindparam('id')).execute(id=self.id)

	def insert(self):
		"""
		insert()

		Inserts an object into the database.
		"""
		self.save(forceinsert=True)

	def protect(self, user):
		"""
		protect(user) -> object

		Returns a version of this object which shows only details which the user is 
		allowed to see.
		"""
		return copy.deepcopy(self)
#}}}
