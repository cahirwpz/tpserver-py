#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.bases import Attribute
from tp.server.rules.base.parameters import AbsCoordParam

class WormholeAttributes( object ):
	end = Attribute(
			type		= AbsCoordParam,
			level		= 'public',
			description	= "Target location of the wormhole." )

class Wormhole( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Object ):
		mapper( cls, inherits = Object, polymorphic_identity = 'Wormhole' )

	@property
	def end( self ):
		return self['end'].position

	@end.setter
	def end( self, value ):
		try:
			self['end'].position = value
		except KeyError:
			AbsCoordParam = self.__game__.objects.use('AbsCoordParam')

			self['end'] = AbsCoordParam( position = value )

	@property
	def	typeno( self ):
		return 4
#}}}

__all__ = [ 'Wormhole' ]
