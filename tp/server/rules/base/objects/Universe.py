#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.bases import Attribute
from tp.server.rules.base.parameters import NumberParam

class UniverseAttributes( object ):
	turn = Attribute(
			type		= NumberParam,
			default		= 0,
			level		= 'public',
			description	= "How many turns has passed in the universe." )

class Universe( object ):#{{{
	__attributes__ = [ 'age' ]

	@classmethod
	def InitMapper( cls, metadata, Object ):
		mapper( cls, inherits = Object, polymorphic_identity = 'Universe' )
	
	@property
	def age( self ):
		try:
			return self['age'].value
		except KeyError:
			return 0

	@age.setter
	def age( self, value ):
		try:
			self['age'].value = value
		except KeyError:
			NumberParam = self.__game__.objects.use('NumberParam')

			self['age'] = NumberParam( value = value )

	@property
	def typeno( self ):
		return 0
#}}}

__all__ = [ 'Universe' ]
