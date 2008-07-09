
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
				desc="Where to go.")
	}

	def do(self):
		obj = Object(self.oid)
		if not hasattr(obj, "command"):
			print "Could not assign move command because object is not an Overlord"
			self.remove()
			return


		obj.pos = self.pos
		obj.command = 2
		obj.save()
		self.remove()


	def turns(self, turns=0):
		return turns

	def resources(self):
		return []