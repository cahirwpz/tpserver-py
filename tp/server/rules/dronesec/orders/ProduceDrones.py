
from tp import netlib

from tp.server.bases.Object import Object
from tp.server.bases.Order import Order
from tp.server.bases.Message import Message

from tp.server.rules.dronesec.objects.Drone import Drone

class ProduceDrones(Order):
	"""\
Build a new drone."""
	typeno = 2

	attributes = {\
		'ships': Order.Attribute("ships", {}, 'protected', type=netlib.objects.constants.ARG_LIST,
					desc="Build Drones."),
		'name':  Order.Attribute("name", 'New Fleet', 'protected', type=netlib.objects.constants.ARG_STRING,
					desc="The new drone's name.")
	}

	def do(self):
		builder = Object(self.oid)

		if not hasattr(builder, "owner"):
			print "Could not do a build order because it was on an unownable object."
			self.remove()

		if self.turns() > 1:
			# Add another year to worked...
			self.worked += 1
			print "Worked %s, %s left until built." % (self.worked, self.turns())
			self.save()
			return

		# Build new fleet object
		fleet = Object(type='tp.server.rules.dronesec.objects.Drone')

		# Type Fleet
		fleet.parent = builder.id
		fleet.posx = builder.posx
		fleet.posy = builder.posy
		fleet.posz = builder.posz
		fleet.size = 1
		fleet.owner = builder.owner
		fleet.ships = self.ships
		fleet.insert()
		fleet.name = self.name
		fleet.save()

		message = Message()
		message.slot = -1
		message.bid = builder.owner
		message.subject = "Drone built"

		message.body = """\
A new fleet (%s) has been built and is orbiting %s.
It consists of:
""" % (fleet.name, builder.name)

		for type, number in fleet.ships.items():
			if number > 1:
				message.body += "%s %ss" % (number, Drone.DP.name[type])
			else:
				message.body += "%s %s" % (number, Drone.DP.name[type])

		message.insert()

		self.remove()

	def turns(self, turns=0):
		return 0

	def resources(self):
		return []

	def fn_ships(self, value=None):
		if value == None:
			returns = []
			for type, name in Drone.DP.name.items():
				returns.append((type, name, -1))
			return returns, self.ships.items()
		else:
			ships = {}

			try:
				for type, number in value[1]:
					if not type in Drone.DP.name.keys():
						raise ValueError("Invalid type selected")
					ships[type] = number
			except:
				pass

			self.ships = ships

	def fn_name(self, value=None):
		if value == None:
			return (255, self.name)
		else:
			self.name = value[1]
