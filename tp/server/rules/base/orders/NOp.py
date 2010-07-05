#!/usr/bin/env python

from tp.server.bases import Order, Attribute

class NOp( Order ):#{{{
	"""
	Wait around and do nothing...
	"""
	@property
	def typeno( self ):
		return 0

	#attributes = { 'wait': Attribute("wait", 0, 'protected', type=1, desc="How long to wait for.") } #netlib.objects.constants.ARG_TIME 
	
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
