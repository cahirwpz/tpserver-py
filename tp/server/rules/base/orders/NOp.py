
from sbases.Order import Order

class NOp(Order):

	def do(self):
		order.wait -= 1

		if order.wait <= 0:
			order.remove()
		else:
			order.save()

	def turns(self, turns=0):
		return self.wait + turns

	def resources(self):
		return []

Order.types[0] = NOp

