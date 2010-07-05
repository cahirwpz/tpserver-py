#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

def GalaxyClass( Object ):
	"""
	Galaxy class parametrized constructor.
	"""
	class Galaxy( Object ):#{{{
		@classmethod
		def InitMapper( cls, metadata ):
			cls.__table__ = Table( cls.__tablename__, metadata,
					Column( 'object_id',   ForeignKey( Object.id ), index = True, primary_key = True ))

			mapper( cls, cls.__table__, inherits = Object, polymorphic_identity = 'Galaxy' )

		@property
		def typeno( self ):
			return 1
#}}}

	return Galaxy

__all__ = [ 'GalaxyClass' ]
