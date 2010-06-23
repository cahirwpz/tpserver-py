#!/usr/bin/env python

from sqlalchemy import *
from tp.server.db import *

from datetime import datetime

class NoSuchThing( Exception ):#{{{
	pass
#}}}

class AlreadyExists( Exception ):#{{{
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

	def findById( self, _id ):
		session = DatabaseManager().session()

		result = session.query( self.cls ).filter_by( id=_id ).first()

		if result is None:
			raise NoSuchThing
		else:
			return result
#}}}

class SQLBase( object ):#{{{
	Utils = SQLUtils()

	def __init__( self, **kwargs ):
		for key, val in kwargs.items():
			setattr( self, key, val )
#}}}

__all__ = [ 'NoSuchThing', 'AlreadyExists', 'PermissionDenied', 'SQLUtils', 'SQLBase' ]
