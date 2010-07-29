#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.model import ParameterDesc, ParametrizedClass
from tp.server.rules.base.parameters import RangeParam

class MineOrder( object ):#{{{
	"""
	Turn a mineable resource into a surface resource.
	"""
	__metaclass__ = ParametrizedClass

	resource = ParameterDesc(
		type		= RangeParam, 
		default		= dict( value = 0 ),
		level		= 'public',
		description	= "Which resource to dig up." )

	amount = ParameterDesc(
		type		= RangeParam,
		default		= dict( value = 0 ),	
		level		= 'public',
		description	= "How much to dig up." )

	@classmethod
	def InitMapper( cls, metadata, Order ):
		mapper( cls, inherits = Order, polymorphic_identity = 'Mine' )

	@property
	def typeno( self ):
		return 6

	def do( self ):
		pass

	def turns( self, turns = 0 ):
		return turns

	def resources( self ):
		return []
#}}}

__all__ = [ 'MineOrder' ]
