#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

class Galaxy( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Object ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column( 'object_id',   ForeignKey( Object.id ), index = True, primary_key = True ))

		mapper( cls, cls.__table__, inherits = Object, polymorphic_identity = 'Galaxy' )

	@property
	def typeno( self ):
		return 1
#}}}

__all__ = [ 'Galaxy' ]
