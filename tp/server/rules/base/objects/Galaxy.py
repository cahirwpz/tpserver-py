#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

class Galaxy( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Object ):
		mapper( cls, inherits = Object, polymorphic_identity = 'Galaxy' )
#}}}

__all__ = [ 'Galaxy' ]
