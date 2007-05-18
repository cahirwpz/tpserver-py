"""\
Resources require to build stuff.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.db import *
from tp import netlib
from SQL import SQLBase

class Property(SQLBase):
	table = Table('property',
		Column('game', 	       Integer,      nullable=False, index=True),
		Column('id',	       Integer,      nullable=False, index=True, primary_key=True),
		Column('name',	       String(255),  nullable=False, index=True),
		Column('display_name', Binary,       nullable=False),
		Column('desc',         Binary,       nullable=False),
		# FIXME: Should be a SmallInteger...
		Column('rank',         Integer,      nullable=False, default=127),
		Column('calculate',    Binary,       nullable=False),
		Column('requirements', Binary,       nullable=False),
		Column('comment',      Binary,       nullable=False),
		#Column('time',	       DateTime,     nullable=False, index=True, onupdate=func.current_timestamp()),
		Column('time',	       Integer,      nullable=False, index=True, onupdate=func.current_timestamp()),

		ForeignKeyConstraint(['game'], ['game.id']),
	)
	table_category = Table('property_category',
		Column('game', 	    Integer,  nullable=False, index=True),
		Column('property',  Integer,  nullable=False, index=True, primary_key=True),
		Column('category',  Integer,  nullable=False, index=True, primary_key=True),
		Column('comment',   Binary,   nullable=False, default=''),
		#Column('time',	    DateTime, nullable=False, index=True, onupdate=func.current_timestamp()),
		Column('time',	    Integer,  nullable=False, index=True, onupdate=func.current_timestamp()),
		ForeignKeyConstraint(['property'], ['property.id']),
		ForeignKeyConstraint(['category'], ['category.id']),
		ForeignKeyConstraint(['game'],     ['game.id']),
	)

	def categories(self):
		"""\
		categories() -> [id, ...]

		Returns the categories the property is in.
		"""
		t = self.table_category
		results = select([t.c.category], t.c.property==self.id).execute().fetchall()
		return [x['category'] for x in results]

	def to_packet(self, user, sequence):
		# Preset arguments
		return netlib.objects.Property(sequence, self.id, self.time, self.categories(), self.rank, self.name, self.display_name, self.desc, self.calculate, self.requirements)

	def id_packet(cls):
		return netlib.objects.Property_IDSequence
	id_packet = classmethod(id_packet)   

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)

