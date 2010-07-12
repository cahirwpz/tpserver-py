#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.bases import ParameterDesc
from tp.server.rules.base.parameters import AbsCoordParam

class Wormhole( object ):#{{{
	__parameters__ = {
			'end' : ParameterDesc(
				type		= AbsCoordParam,
				level		= 'public',
				description	= "Target location of the wormhole." ) }

	@classmethod
	def InitMapper( cls, metadata, Object ):
		mapper( cls, inherits = Object, polymorphic_identity = 'Wormhole' )

	def __check_end_attribute( self ):
		try:
			self['end']
		except KeyError:
			self['end'] = self.__game__.objects.use('AbsCoordParam')()

	@property
	def end( self ):
		self.__check_end_attribute()

		return self['end'].position

	@end.setter
	def end( self, value ):
		self.__check_end_attribute()

		self['end'].position = value

	@property
	def	typeno( self ):
		return 4
#}}}

__all__ = [ 'Wormhole' ]
