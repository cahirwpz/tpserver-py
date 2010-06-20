#!/usr/bin/env python

from sqlalchemy import *

from tp.server.bases.SQL import SQLBase, SQLUtils

class CategoryUtils( SQLUtils ):#{{{
	def byname(self, name):
		c = self.cls.table.c
		return select([c.id], c.name == name, limit=1).execute().fetchall()[0]['id']
#}}}

class Category( SQLBase ):#{{{
	"""
	Categories which help group things together.
	"""

	Utils = CategoryUtils()

	@classmethod
	def getTable( cls, name, metadata ):
		return Table( name, metadata,
				Column('id',          Integer,     index = True, primary_key = True),
				Column('name',        String(255), nullable = False),
				Column('description', Binary,      nullable = False),
				Column('mtime',       DateTime,    nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

	def __str__(self):
		return "<%s id=%s name=%s>" % (self.__class__.__name__, self.id, self.name)
#}}}

__all__ = [ 'Category' ]
