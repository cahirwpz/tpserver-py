#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.bases import ParameterDesc
from tp.server.rules.base.parameters import AbsCoordParam

class Wormhole( object ):#{{{
	end = ParameterDesc(
			type		= AbsCoordParam,
			level		= 'public',
			description	= "Target location of the wormhole." )

	@classmethod
	def InitMapper( cls, metadata, Object ):
		mapper( cls, inherits = Object, polymorphic_identity = 'Wormhole' )
#}}}

__all__ = [ 'Wormhole' ]
