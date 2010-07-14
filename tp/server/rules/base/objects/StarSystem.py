#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

class StarSystem( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Object ):
		mapper( cls, inherits = Object, polymorphic_identity = 'StarSystem' )
#}}}

__all__ = [ 'StarSystem' ]
