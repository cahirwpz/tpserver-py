
from sbases.Order import Order
from sbases.Message import Message

class BuildFleet(Order):

	def do(self):
		# We need information from the builder...
		builder = Object(self.oid)

		if not hasattr(builder, "owner"):
			# Ekk we can't build an object if we don't have an owner...
			print "Could not do a build order because it was on an unownable object."
			self.remove()
		
		object = Object()

		# Type Fleet
		object.type = 4
		object.name = "New fleet"
		object.size = 1

		# Parent the object
		object.parent = builder.parent
		
		# Put it at the position
		object.posx = builder.posx
		object.posy = builder.posy
		object.posz = builder.posz

		object.velx = 0
		object.vely = 0
		object.velz = 0

		object.owner = builder.owner

		object.save()

		message = Message()
		message.bid = obj.owner
		message.slot = Message.number(message.bid)
		message.subject = "%s built" % object.new
		message.body = """%s has arrive at it's destination.""" % object.new
		message.insert()

	def turns(self, turns=0):
		time = {0:1, 1:2, 2:4}
	
		for type, number in self._ships:
			turns += time[type] * number

		return turns

	def resources(self):
		return []

	def get_ships(self):
		return [(0, "Scout", -1), (1, "Frigate", -1), (2, "Battleship", -1)], self._ships

	def set_ships(self, arguments):
		ship = arguments[1]

		try:
			for type, number in arguments[1]:
				if not type in [0, 1, 2]:
					raise ValueError("Invalid type selected")
		except:
			arguments[1] = []
		self._ships = arguments[1]
		
	ships = property(get_ships, set_ships)

Order.types[2] = BuildFleet
