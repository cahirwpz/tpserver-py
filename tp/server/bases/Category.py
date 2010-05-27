"""
Categories which help group things together.
"""

from sqlalchemy import *

from tp.server.db import *
from tp.server.bases.SQL import SQLBase, SQLUtils

class CategoryUtils( SQLUtils ):#{{{
	def byname(self, name):
		c = self.cls.table.c
		return select([c.id], c.name == name, limit=1).execute().fetchall()[0]['id']
#}}}

class Category( SQLBase ):#{{{
	Utils = CategoryUtils()

	table = Table('category', metadata,
				Column('game',	Integer,     nullable=False, index=True, primary_key=True),
				Column('id',	Integer,     nullable=False, index=True, primary_key=True),
				Column('name',	String(255), nullable=False, index=True),
				Column('desc',	Binary,      nullable=False),
				Column('time',	DateTime,    nullable=False, index=True,
					onupdate = func.current_timestamp(),
					default = func.current_timestamp()),
				ForeignKeyConstraint(['game'], ['game.id']))

	def __str__(self):
		return "<Category id=%s name=%s>" % (self.id, self.name)
#}}}
