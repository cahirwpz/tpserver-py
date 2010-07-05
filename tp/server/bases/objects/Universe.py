#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

def UniverseClass( Object ):
	"""
	Universe class parametrized constructor.
	"""
	class Universe( Object ):#{{{
		@classmethod
		def InitMapper( cls, metadata ):
			cls.__table__ = Table( cls.__tablename__, metadata,
					Column( 'object_id', ForeignKey( Object.id ), index = True, primary_key = True ),
					Column( 'age',       Integer, nullable = False, default = 0 ))

			mapper( cls, cls.__table__, inherits = Object, polymorphic_identity = 'Universe' )

		@property
		def typeno( self ):
			return 0
#}}}

	return Universe

__all__ = [ 'UniverseClass' ]