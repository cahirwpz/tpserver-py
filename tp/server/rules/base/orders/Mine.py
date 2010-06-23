#!/usr/bin/env python

from tp.server.bases import Order, Attribute

class Mine(Order):#{{{
	"""
	Turn a mineable resource into a surface resource.
	"""
	typeno = 6

	attributes = {
			'resource': Attribute("resource", 0, 'public', type=netlib.objects.constants.ARG_RANGE, 
				desc="Which resource to dig up."),
			'amount': Attribute("amount", 0, 'public', type=netlib.objects.constants.ARG_RANGE, 
				desc="How much to dig up.")
			}
	
	def do(self):
		pass

	def turns(self, turns=0):
		return turns

	def resources(self):
		return []
#}}}
