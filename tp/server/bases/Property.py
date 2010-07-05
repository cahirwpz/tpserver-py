#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from SQL import SQLBase, SelectableByName

class Property( SQLBase, SelectableByName ):#{{{
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

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)
#}}}

class PropertyCategory( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Property, Category ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('property_id', ForeignKey( Property.id ), primary_key = True),
				Column('category_id', ForeignKey( Category.id ), primary_key = True),
				Column('comment',     Text, nullable = False, default = ''),
				Column('mtime',	      DateTime, nullable = False, 
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		cols = cls.__table__.c

		Index('idx_%s_property_category' % cls.__tablename__, cols.property_id, cols.category_id)

		mapper( cls, cls.__table__, properties = {
			'property': relation( Property,
				uselist = False,
				backref = backref( 'categories' ),
				cascade = 'all'),
			'category': relation( Category,
				uselist = False,
				backref = backref( 'properties' ),
				cascade = 'all')
			})
#}}}

__all__ = [ 'Property', 'PropertyCategory' ]
