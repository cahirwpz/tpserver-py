#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

def WormholeClass( Object ):
	"""
	Wormhole class parametrized constructor.
	"""
	class Wormhole( Object ):#{{{
		@classmethod
		def InitMapper( cls, metadata ):
			cls.__table__ = Table( cls.__tablename__, metadata,
					Column( 'object_id', ForeignKey( Object.id ), index = True, primary_key = True ),
					Column( 'end_x',     Integer, nullable = False ),
					Column( 'end_y',     Integer, nullable = False ),
					Column( 'end_z',     Integer, nullable = False ))

			mapper( cls, cls.__table__, inherits = Object, polymorphic_identity = 'Wormhole' )

		@property
		def	typeno( self ):
			return 4
#}}}

	return Wormhole

__all__ = [ 'WormholeClass' ]
