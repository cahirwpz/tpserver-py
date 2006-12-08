"""\
Resources require to build stuff.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp import netlib
from SQL import SQLBase

class Resource(SQLBase):
	table = Table('resource',
		Column('id',	       Integer,  nullable=False, default=0, index=True, primary_key=True),
		Column('namesingular', Binary,   nullable=False),
		Column('nameplural',   Binary,   nullable=False),
		Column('unitsingular', Binary,   nullable=False),
		Column('unitplural',   Binary,   nullable=False),
		Column('desc',         Binary,   nullable=False),
		Column('weight',       Integer,  nullable=False, default=0),
		Column('size',         Integer,  nullable=False, default=0),
		Column('time',	       DateTime, nullable=False, index=True, onupdate=func.current_timestamp()),
	)

	def to_packet(self, sequence):
		return netlib.objects.Resource(sequence, self.id, self.name_singular, self.name_pludesc, Resource.number(self.id))

	def id_packet(cls):
		return netlib.objects.Resource_IDSequence
	id_packet = classmethod(id_packet)

	def __str__(self):
		return "<Resource id=%s>" % (self.id)

