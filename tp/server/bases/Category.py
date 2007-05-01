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
	table = Table('category',
		Column('game',	Integer,     nullable = False, index=True),
		Column('id',	Integer,     nullable = False, index=True, primary_key=True),
		Column('name',	String(255), nullable = False, index=True),
		Column('desc',	Binary,      nullable = False),
		Column('time',	DateTime,    nullable = False, index=True, onupdate=func.current_timestamp()),
	)

	def to_packet(self, sequence):
		# Preset arguments
		return netlib.objects.Category(sequence, self.id, self.time, self.name, self.desc)
	
	def id_packet(cls):
		return netlib.objects.Category_IDSequence
	id_packet = classmethod(id_packet)

	def __str__(self):
		return "<Category id=%s name=%s>" % (self.id, self.name)

