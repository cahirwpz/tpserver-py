"""Contains the Stop Order"""
from tp import netlib
from tp.server.bases.Order import Order
from tp.server.bases.Object import Object

class Stop(Order):
	"""\
Make Drones stop moving...
"""
	typeno = 106

	attributes = {\
		'wait': Order.Attribute("wait", 0, 'protected', type=netlib.objects.constants.ARG_TIME,
				desc="How long to wait for.")
	}

	def do(self):
		"""
		Executes Stop
		Sets the overlords command parameters to stop
		"""
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