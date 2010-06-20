#!/usr/bin/env python

from sqlalchemy import *

from SQL import SQLUtils, NoSuchThing, SQLBase

class ResourceUtils( SQLUtils ):#{{{
	def byname(self, name):
		c = self.cls.table.c
		try:
			return select([c.id], c.namesingular == name, limit=1).execute().fetchall()[0]['id']
		except IndexError:
			raise NoSuchThing("No object with name (either singular or plural) %s" % name)
#}}}

class Resource( SQLBase ):#{{{
	"""
	Resources require to build stuff.
	"""

	Utils = ResourceUtils()

	@classmethod
	def getTable( cls, name, metadata ):
		return Table( name, metadata,
				Column('id',	       Integer,  index = True, primary_key = True),
				Column('type',	       String(255), nullable = False),
				Column('name_singular', Binary,   nullable = False),
				Column('name_plural',   Binary,   nullable = False, default = ''),
				Column('unit_singular', Binary,   nullable = False, default = ''),
				Column('unit_plural',   Binary,   nullable = False, default = ''),
				Column('description',  Binary,   nullable = False),
				Column('weight',       Integer,  nullable = False, default = 0),
				Column('size',         Integer,  nullable = False, default = 0),
				Column('mtime',	       DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

	def __str__(self):
		return "<Resource id=%s>" % (self.id)
#}}}

__all__ = [ 'Resource' ]
