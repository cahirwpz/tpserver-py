#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from Model import ModelObject, ByNameMixin

class Property( ModelObject, ByNameMixin ):#{{{
	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',	       Integer, index = True, primary_key = True),
				Column('name',	       String(255), index = True, nullable = False),
				Column('display_name', Text, nullable = False),
				Column('description',  Text, nullable = False),
				Column('rank',         Integer, nullable = False, default=127), # FIXME: Should be a SmallInteger...
				Column('calculate',    Text, nullable = False),
				Column('requirements', Text, nullable = False, default="""(lambda (design) (cons #t ""))"""),
				Column('comment',      Text, nullable = False, default=''),
				Column('mtime',	       DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()),
				UniqueConstraint( 'name' ))

		mapper( cls, cls.__table__ )

	def remove( self, session ):
		for category in self.categories:
			category.remove( session )

		session.commit()

		session.delete( self )

	def __str__( self ):
		return '<%s@%s id="%s" name="%s">' % ( self.__origname__, self.__game__.name, self.id, self.name )
#}}}

class PropertyCategory( ModelObject ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Property, Category ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('property_id', ForeignKey( Property.id ), primary_key = True),
				Column('category_id', ForeignKey( Category.id ), primary_key = True),
				Column('comment',     Text, nullable = False, default = ''),
				Column('mtime',	      DateTime, nullable = False, 
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		cols = cls.__table__.c

		Index('ix_%s_property_category' % cls.__tablename__, cols.property_id, cols.category_id)

		mapper( cls, cls.__table__, properties = {
			'property': relation( Property,
				uselist = False,
				backref = backref( 'categories' )),
			'category': relation( Category,
				uselist = False,
				backref = backref( 'properties' ))
			})
#}}}

__all__ = [ 'Property', 'PropertyCategory' ]
