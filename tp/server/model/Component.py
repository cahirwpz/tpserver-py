#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref, class_mapper

from Model import ModelObject, ByNameMixin

class Component( ModelObject, ByNameMixin ):
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
		for prop in self.properties:
			prop.remove( session )

		session.commit()

		session.delete( self )

	def __str__( self ):
		return '<%s@%s id="%s" name="%s">' % ( self.__origname__, self.__game__.name, self.id, self.name )

class ComponentCategory( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata, Component, Category ):
		cls.__table__ = Table( cls.__tablename__, metadata, 
				Column('component_id', ForeignKey( Component.id ), primary_key = True),
				Column('category_id',  ForeignKey( Category.id ), primary_key = True))

		cols = cls.__table__.c

		Index('ix_%s_component_category' % cls.__tablename__, cols.component_id, cols.category_id)

		mapper( cls, cls.__table__, properties = {
			'component': relation( Component,
				uselist = False ),
			'category': relation( Category,
				uselist = False )
			})

		class_mapper( Component ).add_property( 'categories',
			relation( Category,
				secondary = cls.__table__,
				backref = backref( 'components' )))

	def __str__( self ):
		return '<%s@%s id="%s" component="%s", category="%s">' % \
				( self.__origname__, self.__game__.name, self.component.name, self.category.name )

class ComponentProperty( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata, Component, Property ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('component_id', ForeignKey( Component.id ), primary_key = True ),
				Column('property_id',  ForeignKey( Property.id ), primary_key = True ),
				Column('value',        Text, nullable = False, default = """(lambda (design) 1)""" ))

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

	def __str__( self ):
		return '<%s@%s id="%s" component="%s", property="%s">' % \
				( self.__origname__, self.__game__.name, self.component.name, self.property.name )

__all__ = [ 'Component', 'ComponentCategory', 'ComponentProperty' ]
