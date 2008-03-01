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
	table = Table('property', metadata,
		Column('game', 	       Integer,      nullable=False, index=True, primary_key=True),
		Column('id',	       Integer,      nullable=False, index=True, primary_key=True),
		Column('name',	       String(255),  nullable=False, index=True),
		Column('displayname',  Binary,       nullable=False),
		Column('desc',         Binary,       nullable=False),
		# FIXME: Should be a SmallInteger...
		Column('rank',         Integer,      nullable=False, default=127),
		Column('calculate',    Binary,       nullable=False),
		Column('requirements', Binary,       nullable=False, default="""(lambda (design) (cons #t ""))"""),
		Column('comment',      Binary,       nullable=False, default=''),
		Column('time',	       DateTime,     nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		ForeignKeyConstraint(['game'], ['game.id']),
	)
	table_category = Table('property_category', metadata,
		Column('game', 	    Integer,  nullable=False, index=True, primary_key=True),
		Column('property',  Integer,  nullable=False, index=True, primary_key=True),
		Column('category',  Integer,  nullable=False, index=True, primary_key=True),
		Column('comment',   Binary,   nullable=False, default=''),
		Column('time',	    DateTime, nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		ForeignKeyConstraint(['property'], ['property.id']),
		ForeignKeyConstraint(['category'], ['category.id']),
		ForeignKeyConstraint(['game'],     ['game.id']),
	)

	@classmethod
	def byname(cls, name):
		c = cls.table.c
		return select([c.id], c.name == name, limit=1).execute().fetchall()[0]['id']

	def get_categories(self):
		"""\
		categories() -> [id, ...]

		Returns the categories the property is in.
		"""
		t = self.table_category
		results = select([t.c.category], t.c.property==self.id).execute().fetchall()
		return [x['category'] for x in results]

	def to_packet(self, user, sequence):
		# Preset arguments
		return netlib.objects.Property(sequence, self.id, self.time, self.categories, self.rank, self.name, self.displayname, self.desc, self.calculate, self.requirements)

	@classmethod
	def id_packet(cls):
		return netlib.objects.Property_IDSequence

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)

	def load(self, id):
		"""\
		load(id)

		Loads a thing from the database.
		"""
		SQLBase.load(self, id)

		# Load the categories now
		self.categories = self.get_categories()

	def save(self, forceinsert=False):
		"""\
		save()

		Saves a thing to the database.
		"""
		SQLBase.save(self, forceinsert)

		# Save the categories now
		t = self.table_category
		current = self.get_categories()
		for cid in current+self.categories:
			if (cid in current) and (not cid in self.categories):
				# Remove the category
				results = delete(t, (t.c.property==self.id) & (t.c.category==cid)).execute()
			
			if (not cid in current) and (cid in self.categories):
				# Add the category
				results = insert(t).execute(property=self.id, category=cid)

