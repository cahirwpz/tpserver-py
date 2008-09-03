"""\
Categories which help group things together.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.db import *
from tp import netlib
from SQL import SQLBase

class Category(SQLBase):
	table = Table('category', metadata,
		Column('game',	Integer,     nullable=False, index=True, primary_key=True),
		Column('id',	Integer,     nullable=False, index=True, primary_key=True),
		Column('name',	String(255), nullable=False, index=True),
		Column('desc',	Binary,      nullable=False),
		Column('time',	DateTime,    nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		ForeignKeyConstraint(['game'], ['game.id']),
	)

	@classmethod
	def byname(cls, name):
		"""\
		byname(name)
		
		Returns the objects with a certain name
		"""
		c = cls.table.c
		return select([c.id], c.name == name, limit=1).execute().fetchall()[0]['id']

	def to_packet(self, user, sequence):
		# Preset arguments
		return netlib.objects.Category(sequence, self.id, self.time, self.name, self.desc)
	
	@classmethod
	def id_packet(cls):
		return netlib.objects.Category_IDSequence

	def __str__(self):
		return "<Category id=%s name=%s>" % (self.id, self.name)

