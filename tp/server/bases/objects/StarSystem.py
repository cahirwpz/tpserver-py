#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

def StarSystemClass( Object ):
	"""
	System class parametrized constructor.
	"""
	class StarSystem( Object ):#{{{
		@classmethod
		def InitMapper( cls, metadata ):
			cls.__table__ = Table( cls.__tablename__, metadata,
					Column( 'object_id',   ForeignKey( Object.id ), index = True, primary_key = True ))

			mapper( cls, cls.__table__, inherits = Object, polymorphic_identity = 'StarSystem' )

		@property
		def typeno( self ):
			return 2
	#}}}

	return StarSystem

__all__ = [ 'StarSystemClass' ]
