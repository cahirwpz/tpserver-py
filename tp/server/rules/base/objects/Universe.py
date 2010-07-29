#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.model import ParameterDesc, ParametrizedClass
from tp.server.rules.base.parameters import NumberParam

class Universe( object ):#{{{
	__metaclass__  = ParametrizedClass

	age = ParameterDesc(
			type		= NumberParam,
			default		= 0,
			level		= 'public',
			description	= "How many turns has passed in the universe." )

	@classmethod
	def InitMapper( cls, metadata, Object ):
		mapper( cls, inherits = Object, polymorphic_identity = 'Universe' )
#}}}

__all__ = [ 'Universe' ]
