"""
Components which can be put together to form designs.
"""

from sqlalchemy import *

from tp.server.db import *
from tp.server.bases.SQL import SQLTypedBase, SQLTypedTable

class Component(SQLTypedBase):#{{{
	table = Table('component', metadata,
				Column('game', 	  Integer,     nullable=False, index=True, primary_key=True),
				Column('id',	  Integer,     nullable=False, index=True, primary_key=True),
				Column('type',	  String(255), nullable=False, index=True),
				Column('name',	  String(255), nullable=False, index=True),
				Column('desc',    Binary,      nullable=False),
				Column('requirements', Binary, nullable=False, default="""(lambda (design) (cons #t ""))"""),
				Column('comment', Binary,      nullable=False, default=''),
				Column('time',	  DateTime,    nullable=False, index=True,
					onupdate = func.current_timestamp(),
					default = func.current_timestamp()),
				ForeignKeyConstraint(['game'], ['game.id']))

	table_extra = SQLTypedTable('component')

	table_category = Table('component_category', metadata,
				Column('game', 		Integer,  nullable=False, index=True, primary_key=True),
				Column('component', Integer,  nullable=False, index=True, primary_key=True),
				Column('category',  Integer,  nullable=False, index=True, primary_key=True),
				Column('comment',   Binary,   nullable=False, default=''),
				Column('time',	    DateTime, nullable=False, index=True,
					onupdate = func.current_timestamp(),
					default = func.current_timestamp()),
				ForeignKeyConstraint(['component'], ['component.id']),
				ForeignKeyConstraint(['category'],  ['category.id']),
				ForeignKeyConstraint(['game'],      ['game.id']))

	table_property = Table('component_property', metadata,
				Column('game', 		Integer,  nullable=False, index=True, primary_key=True),
				Column('component', Integer,  nullable=False, index=True, primary_key=True),
				Column('property',  Integer,  nullable=False, index=True, primary_key=True),
				Column('value',     Binary,   nullable=False, default='(lambda (design) 1)'),
				Column('comment',   Binary,   nullable=False, default=''),
				Column('time',	    DateTime, nullable=False, index=True,
					onupdate = func.current_timestamp(),
					default = func.current_timestamp()),
				ForeignKeyConstraint(['component'], ['component.id']),
				ForeignKeyConstraint(['property'],  ['property.id']),
				ForeignKeyConstraint(['game'],      ['game.id']))

	@classmethod
	def byname(cls, name):
		c = cls.table.c
		return select([c.id], c.name == name, limit=1).execute().fetchall()[0]['id']

	def get_categories( self ):
		"""
		categories() -> [id, ...]

		Returns the categories the component is in.
		"""
		t = self.table_category
		results = select([t.c.category], t.c.component==self.id).execute().fetchall()
		return [x['category'] for x in results]

	def def_properties( self ):
		"""
		get_properties() -> [(id, value), ...]

		Returns the properties the component has.
		"""
		t = self.table_property
		results = select([t.c.property, t.c.value], t.c.component==self.id).execute().fetchall()
		return [(x['property'], x['value']) for x in results]

	def property(self, id):
		"""
		property(property_id) -> property_value_function

		Returns the property value function for this component given a property id
		"""
		t = self.table_property
		results = select([t.c.value], (t.c.component==self.id) & (t.c.property==id)).execute().fetchall()
		if len(results) == 1:
			return results[0]['value']

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)

	def load(self, id):
		"""
		load(id)

		Loads a thing from the database.
		"""
		SQLTypedBase.load(self, id)

		# Load the categories now
		self.categories = self.get_categories()

		# Load the properties now
		self.properties = self.get_properties()
	
	def save(self, forceinsert=False):
		"""
		save()

		Saves a thing to the database.
		"""
		SQLTypedBase.save(self, forceinsert)

		# Save the categories now
		t = self.table_category
		current = self.get_categories()
		for cid in current+self.categories:
			if (cid in current) and (not cid in self.categories):
				# Remove the category
				results = delete(t, (t.c.component==self.id) & (t.c.category==cid)).execute()
			
			if (not cid in current) and (cid in self.categories):
				# Add the category
				results = insert(t).execute(component=self.id, category=cid)

		# Save the Properties now
		t = self.table_property
		current = self.get_properties()
		for cid in current+self.properties.keys():
			if (cid in current) and (not cid in self.properties.keys()):
				# Remove the category
				results = delete(t, (t.c.component==self.id) & (t.c.property==cid)).execute()
			
			elif (not cid in current) and (cid in self.properties.keys()):
				# Add the category
				results = insert(t).execute(component=self.id, property=cid, value=self.properties[cid])

			else:
				# Update the property
				results = update(t, (t.c.component==self.id) & (t.c.property==cid)).execute(component=self.id, property=cid, value=self.properties[cid])
#}}}
