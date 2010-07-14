#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.bases import ParameterDesc, ParametrizedClass
from tp.server.rules.base.parameters import TimeParam

class WaitOrder( object ):#{{{
	"""
	Wait around and do nothing...
	"""
	__metaclass__ = ParametrizedClass

	wait = ParameterDesc(
			default		= 0,
			level		= 'protected',
			type		= TimeParam,
			description	= "How long to wait for." )

	@classmethod
	def InitMapper( cls, metadata, Order ):
		mapper( cls, inherits = Order, polymorphic_identity = 'Wait' )

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

__all__ = [ 'WaitOrder' ]
