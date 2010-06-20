#!/usr/bin/env python

from sqlalchemy import *

from SQL import SQLBase, SQLUtils

class PropertyUtils( SQLUtils ):#{{{
	def byname(self, name):
		c = self.cls.table.c
		return select([c.id], c.name == name, limit=1).execute().fetchall()[0]['id']
#}}}

class Property( SQLBase ):#{{{
	Utils = PropertyUtils()

	@classmethod
	def getTable( cls, name, metadata ):
		return Table( name, metadata,
				Column('id',	       Integer,      index = True, primary_key = True),
				Column('name',	       String(255),  nullable = False),
				Column('display_name', Binary,       nullable = False),
				Column('description',  Binary,       nullable = False),
				Column('rank',         Integer,      nullable = False, default=127), # FIXME: Should be a SmallInteger...
				Column('calculate',    Binary,       nullable = False),
				Column('requirements', Binary,       nullable = False, default="""(lambda (design) (cons #t ""))"""),
				Column('comment',      Binary,       nullable = False, default=''),
				Column('mtime',	       DateTime,     nullable = False,
					onupdate = func.current_timestamp(),
					default = func.current_timestamp()))

	def get_categories(self):
		"""
		categories() -> [id, ...]

		Returns the categories the property is in.
		"""
		t = self.table_category
		results = select([t.c.category], t.c.property==self.id).execute().fetchall()
		return [x['category'] for x in results]

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
#}}}

class PropertyCategory( SQLBase ):#{{{
	@classmethod
	def getTable( cls, name, metadata, property_table, category_table ):
		return Table( name, metadata,
				Column('id',        Integer,  index = True, primary_key = True),
				Column('property',  ForeignKey( '%s.id' % property_table ), nullable = False),
				Column('category',  ForeignKey( '%s.id' % category_table), nullable = False),
				Column('comment',   Binary,   nullable = False, default = ''),
				Column('mtime',	    DateTime, nullable = False, 
					onupdate = func.current_timestamp(),
					default = func.current_timestamp()))
#}}}

__all__ = [ 'Property', 'PropertyCategory' ]
