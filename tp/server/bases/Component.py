"""\
Components which can be put together to form designs.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.db import *
from tp import netlib
from SQL import SQLBase

class Component(SQLBase):
	table = Table('component',
		Column('game', 	  Integer,     nullable=False, index=True, primary_key=True),
		Column('id',	  Integer,     nullable=False, index=True, primary_key=True),
		Column('name',	  String(255), nullable=False, index=True),
		Column('desc',    Binary,      nullable=False),
		Column('requirements', Binary, nullable=False),
		Column('comment', Binary,      nullable=False),
		Column('time',	  DateTime,    nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		ForeignKeyConstraint(['game'], ['game.id']),
	)
	table_category = Table('component_category',
		Column('game', 		Integer,  nullable=False, index=True, primary_key=True),
		Column('component', Integer,  nullable=False, index=True, primary_key=True),
		Column('category',  Integer,  nullable=False, index=True, primary_key=True),
		Column('comment',   Binary,   nullable=False, default=''),
		Column('time',	    DateTime, nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		ForeignKeyConstraint(['component'], ['component.id']),
		ForeignKeyConstraint(['category'],  ['category.id']),
		ForeignKeyConstraint(['game'],      ['game.id']),
	)
	table_property = Table('component_property',
		Column('game', 		Integer,  nullable=False, index=True, primary_key=True),
		Column('component', Integer,  nullable=False, index=True, primary_key=True),
		Column('property',  Integer,  nullable=False, index=True, primary_key=True),
		Column('value',     Binary,   nullable=False, default=''),
		Column('comment',   Binary,   nullable=False, default=''),
		Column('time',	    DateTime, nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		ForeignKeyConstraint(['component'], ['component.id']),
		ForeignKeyConstraint(['property'],  ['property.id']),
		ForeignKeyConstraint(['game'],      ['game.id']),
	)

	def categories(self):
		"""\
		categories() -> [id, ...]

		Returns the categories the component is in.
		"""
		t = self.table_category
		results = select([t.c.category], t.c.component==self.id).execute().fetchall()
		return [x['category'] for x in results]

	def properties(self):
		"""\
		properties() -> [(id, value), ...]

		Returns the properties the component has.
		"""
		t = self.table_property
		results = select([t.c.property, t.c.value], t.c.component==self.id).execute().fetchall()
		return [(x['property'], x['value']) for x in results]

	def property(self, id):
		"""\
		property(property_id) -> property_value_function

		Returns the property value function for this component given a property id
		"""
		t = self.table_property
		results = select([t.c.value], (t.c.component==self.id) & (t.c.property==id)).execute().fetchall()
		if len(results) == 1:
			return results[0]['value']
		return None

	def to_packet(self, user, sequence):
		print "to_packet", [self.id, self.time, self.categories(), self.name, self.desc, self.requirements, self.properties()]
		return netlib.objects.Component(sequence, self.id, self.time, self.categories(), self.name, self.desc, self.requirements, self.properties())

	def id_packet(cls):
		return netlib.objects.Component_IDSequence
	id_packet = classmethod(id_packet)   

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)

