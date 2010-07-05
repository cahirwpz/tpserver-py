#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from SQL import SQLBase, SelectableByName

class Component( SQLBase, SelectableByName ):#{{{
	"""
	Components which can be put together to form designs.
	"""

	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',           Integer, index = True, primary_key = True),
				Column('name',         String(255), nullable = False),
				Column('description',  Text, nullable = False),
				Column('requirements', Text, nullable = False, default = """(lambda (design) (cons #t ""))"""),
				Column('comment',      Text, nullable = False, default = ''),
				Column('mtime',        DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		mapper( cls, cls.__table__ )

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)
#}}}

class ComponentCategory( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Component, Category ):
		cls.__table__ = Table( cls.__tablename__, metadata, 
				Column('component_id', ForeignKey( Component.id ), primary_key = True),
				Column('category_id',  ForeignKey( Category.id ), primary_key = True),
				Column('comment',      Text, nullable = False, default = ''),
				Column('mtime',	       DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		cols = cls.__table__.c

		Index('idx_%s_component_category' % cls.__tablename__, cols.component_id, cols.category_id)

		mapper( cls, cls.__table__, properties = {
			'component': relation( Component,
				uselist = False,
				backref = backref( 'categories' ),
				cascade = 'all'),
			'category': relation( Category,
				uselist = False,
				backref = backref( 'components' ),
				cascade = 'all')
			})
#}}}

class ComponentProperty( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Component, Property ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('component_id', ForeignKey( Component.id ), primary_key = True ),
				Column('property_id',  ForeignKey( Property.id ), primary_key = True ),
				Column('value',        Text, nullable = False, default = """(lambda (design) 1)""" ),
				Column('comment',      Text, nullable = False, default = '' ),
				Column('mtime',        DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		cols = cls.__table__.c

		Index('idx_%s_component_property' % cls.__tablename__, cols.component_id, cols.property_id)

		mapper( cls, cls.__table__, properties = {
			'component': relation( Component,
				uselist = False,
				backref = backref( 'properties' ),
				cascade = 'all'),
			'property': relation( Property,
				uselist = False,
				backref = backref( 'components' ),
				cascade = 'all')
			})
#}}}

__all__ = [ 'Component', 'ComponentCategory', 'ComponentProperty' ]
