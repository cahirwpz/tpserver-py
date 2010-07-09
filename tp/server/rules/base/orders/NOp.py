#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

class NOpOrder( object ):#{{{
	"""
	Wait around and do nothing...
	"""

	@classmethod
	def InitMapper( cls, metadata, Order ):
		mapper( cls, inherits = Order, polymorphic_identity = 'NOp' )

		#attributes = { 'wait': Attribute("wait", 0, 'protected', type=1, desc="How long to wait for.") } #netlib.objects.constants.ARG_TIME 

	@property
	def typeno( self ):
		return 0
	
	def do(self):
		self.wait -= 1

		if self.wait <= 0:
			self.remove()
		else:
			self.save()

	def turns(self, turns=0):
		return self.wait + turns

	def resources(self):
		return []
	
	def fn_wait(self, value=None):
		if value is None:
			return self.wait, -1
		else:
			self.wait = value[0]
#}}}

__all__ = [ 'NOpOrder' ]
