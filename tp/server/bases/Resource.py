"""
Resources require to build stuff.
"""

from sqlalchemy import *

from tp.server.db import *
from tp.server.bases.SQL import SQLUtils, NoSuchThing
from tp.server.bases.SQLTypedBase import SQLTypedBase, SQLTypedTable

class ResourceUtils( SQLUtils ):#{{{
	def byname(self, name):
		c = self.cls.table.c
		try:
			return select([c.id], c.namesingular == name, limit=1).execute().fetchall()[0]['id']
		except IndexError:
			raise NoSuchThing("No object with name (either singular or plural) %s" % name)
#}}}

class Resource( SQLTypedBase ):#{{{
	Utils = ResourceUtils()

	table = Table('resource', metadata,
				Column('game', 	       Integer,  nullable=False, index=True, primary_key=True),
				Column('id',	       Integer,  nullable=False, index=True, primary_key=True),
				Column('type',	       String(255), nullable=False, index=True),
				Column('namesingular', Binary,   nullable=False),
				Column('nameplural',   Binary,   nullable=False, default=''),
				Column('unitsingular', Binary,   nullable=False, default=''),
				Column('unitplural',   Binary,   nullable=False, default=''),
				Column('desc',         Binary,   nullable=False),
				Column('weight',       Integer,  nullable=False, default=0),
				Column('size',         Integer,  nullable=False, default=0),
				Column('time',	       DateTime, nullable=False, index=True,
					onupdate = func.current_timestamp(),
					default=func.current_timestamp()),
				ForeignKeyConstraint(['game'], ['game.id']))

	table_extra = SQLTypedTable('resource')

	def __str__(self):
		return "<Resource id=%s>" % (self.id)
#}}}
