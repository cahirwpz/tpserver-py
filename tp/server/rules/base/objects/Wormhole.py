#!/usr/bin/env python

from tp.server.model import ParameterDesc, ParametrizedClass
from tp.server.rules.base.parameters import AbsCoordParam

class Wormhole( object ):#{{{
	__metaclass__  = ParametrizedClass

	end = ParameterDesc(
			type		= AbsCoordParam,
			level		= 'public',
			description	= "Target location of the wormhole." )
#}}}

__all__ = [ 'Wormhole' ]
