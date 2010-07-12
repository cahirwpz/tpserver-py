#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref
from sqlalchemy.orm.collections import attribute_mapped_collection

from SQL import SQLBase

class ObjectAttribute( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Object, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('object_id', ForeignKey( Object.id ), index = True, primary_key = True ),
				Column('name',      String( 255 ), index = True, primary_key = True ),
				Column('param_id',  ForeignKey( Parameter.id ), nullable = True ),
				UniqueConstraint( 'object_id', 'name' ))

		mapper( cls, cls.__table__, properties = {
			'object' : relation( Object,
				uselist = False,
				backref = backref( 'attributes',
					collection_class = attribute_mapped_collection( 'name' ))
				),
			'param' : relation( Parameter,
				uselist = False )
			})
	#}}}

from collections import MutableMapping

class AttributeDictMixin( MutableMapping ):#{{{
	_row_type		= None

	__map	= property( lambda self: self.attributes )

	def __getitem__( self, key ):
		return self.__map[ key ].param

	def __setitem__( self, key, value ):
		item = self.__map.get( key, None )

		if item is None:
			self.__map[ key ] = self._row_type( name = key, param = value )
		else:
			item.param = value

	def __delitem__(self, key):
		del self.__map[ key ]

	def __contains__( self, key ):
		return key in self.__map

	def __iter__( self ):
		return self.__map.__iter__()

	def __len__( self ):
		return self.__map.__len__()
#}}}

class Attribute( object ):#{{{
	def __init__( self, type, level, default = None, description = None ):
		self.type			= type
		self.level			= level
		self.default		= default
		self.description	= description
#}}}

__all__ = [ 'Attribute', 'ObjectAttribute', 'AttributeDictMixin' ]
