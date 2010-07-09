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

__all__ = [ 'Wormhole' ]
