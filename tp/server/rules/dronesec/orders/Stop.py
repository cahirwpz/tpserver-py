from tp import netlib
from tp.server.bases.Order import Order

class Stop(Order):
	"""\
Make Drones stop moving...
"""
	typeno = 6

	attributes = {\
		'wait': Order.Attribute("wait", 0, 'protected', type=netlib.objects.constants.ARG_TIME,
				desc="How long to wait for.")
	}

	def do(self):
		obj = Object(self.oid)
		if not hasattr(obj, "command"):
			print "Could not assign move command because object is not an Overlord"
			self.remove()
			return

		obj.command = 0
		obj.save()
		self.remove()

	def turns(self, turns=0):
		return self.wait + turns

	def resources(self):
		return []

	def fn_wait(self, value=None):
		if value is None:
			return self.wait, -1
		else:
			self.wait = value[0]