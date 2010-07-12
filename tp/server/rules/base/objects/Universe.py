#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.bases import ParameterDesc
from tp.server.rules.base.parameters import NumberParam

class Universe( object ):#{{{
	__parameters__ = {
			'age' : ParameterDesc(
				type		= NumberParam,
				default		= 0,
				level		= 'public',
				description	= "How many turns has passed in the universe." ) }

	@classmethod
	def InitMapper( cls, metadata, Object ):
		mapper( cls, inherits = Object, polymorphic_identity = 'Universe' )

	def __check_age_attribute( self ):
		try:
			self['age']
		except KeyError:
			self['age'] = self.__game__.objects.use('NumberParam')()
	
	@property
	def age( self ):
		self.__check_age_attribute()

		return self['age'].value

	@age.setter
	def age( self, value ):
		self.__check_age_attribute()

		self['age'].value = value

	@property
	def typeno( self ):
		return 0
#}}}

__all__ = [ 'Universe' ]
