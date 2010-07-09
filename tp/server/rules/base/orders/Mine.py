#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

class MineOrder( object ):#{{{
	"""
	Turn a mineable resource into a surface resource.
	"""

	@classmethod
	def InitMapper( cls, metadata, Order ):
		mapper( cls, inherits = Order, polymorphic_identity = 'Mine' )

	# attributes = {
	#		'resource': Attribute("resource", 0, 'public', type=netlib.objects.constants.ARG_RANGE, 
	#			desc="Which resource to dig up."),
	#		'amount': Attribute("amount", 0, 'public', type=netlib.objects.constants.ARG_RANGE, 
	#			desc="How much to dig up.")
	#		}
	
	@property
	def typeno( self ):
		return 6

	def do(self):
		pass

	def turns(self, turns=0):
		return turns

	def resources(self):
		return []
#}}}

__all__ = [ 'MineOrder' ]
