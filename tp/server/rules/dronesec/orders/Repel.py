
from tp import netlib

from tp.server.bases.Order import Order
from tp.server.bases.Object import Object
from tp.server.bases.Message import Message


class Repel(Order):
	"""\
Drones move to a point in space.
"""
	typeno = 104
	attributes = {\
		'pos': Order.Attribute("pos", (0,0,0), 'public', type=netlib.objects.constants.ARG_ABS_COORD,
				desc="Where to go."),
		'wait': Order.Attribute("wait", 0, 'protected', type = netlib.objects.constants.ARG_TIME,
				desc = "How long to wait before attracting"),
	}

	def do(self):
		obj = Object(self.oid)
		if not hasattr(obj, "command"):
			print "Could not assign move command because object is not an Overlord"
			self.remove()
			return


		if self.wait <= 1:
			obj.pos = self.pos
			obj.command = 2
			obj.save()
		else:
			self.wait -= 1
			self.save()



	def fn_wait(self, value=None):
		if value is None:
			return self.wait, -1
		else:
			self.wait = value[0]



	def turns(self, turns=0):
		return turns + self.wait

	def resources(self):
		return []