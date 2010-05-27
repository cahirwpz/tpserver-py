
from tp import netlib
from tp.server.bases.Order import Order

class NOp(Order):
	"""\
Wait around and do nothing...
"""
	typeno = 0

	attributes = {\
		'wait': Order.Attribute("wait", 0, 'protected', type=1, #netlib.objects.constants.ARG_TIME, 
				desc="How long to wait for.")
	}
	
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
