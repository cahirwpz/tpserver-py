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

	def remove( self, session ):
		for category in self.categories:
			category.remove( session )

		for property in self.properties:
			property.remove( session )

		session.commit()

		session.delete( self )

	def __str__(self):
		return '<%s@%s id="%d" name="%s">' % ( self.__origname__, self.__game__.__name__, self.id, self.name )
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

		Index('ix_%s_component_category' % cls.__tablename__, cols.component_id, cols.category_id)

		mapper( cls, cls.__table__, properties = {
			'component': relation( Component,
				uselist = False,
				backref = backref( 'categories' )),
			'category': relation( Category,
				uselist = False,
				backref = backref( 'components' ))
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

		Index('ix_%s_component_property' % cls.__tablename__, cols.component_id, cols.property_id)

		mapper( cls, cls.__table__, properties = {
			'component': relation( Component,
				uselist = False,
				backref = backref( 'properties' )),
			'property': relation( Property,
				uselist = False,
				backref = backref( 'components' ))
			})
#}}}

__all__ = [ 'Component', 'ComponentCategory', 'ComponentProperty' ]
