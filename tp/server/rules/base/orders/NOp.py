
from sbases.Order import Order

class NOp(Order):

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

Order.types[0] = NOp

