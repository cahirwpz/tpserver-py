
from config import netlib
from tp.server.bases.Order import Order

class NOp(Order):
	"""\
Wait around and do nothing...
"""

	attributes = {\
		'wait': Order.Attribute("wait", 0, 'public', type=netlib.objects.constants.ARG_TIME, 
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

NOp.typeno = 0
Order.types[NOp.typeno] = NOp
