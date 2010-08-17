#!/usr/bin/env python

from tp.server.model import ParameterDesc, ParametrizedClass
from tp.server.rules.base.parameters import NumberParam

class Universe( object ):
	__metaclass__  = ParametrizedClass

	age = ParameterDesc(
			type		= NumberParam,
			default		= 0,
			level		= 'public',
			description	= "How many turns has passed in the universe." )

__all__ = [ 'Universe' ]
