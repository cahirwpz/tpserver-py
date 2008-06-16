
from tp import netlib

from tp.server.bases.Object import Object
from tp.server.bases.Order import Order
from tp.server.bases.Message import Message
from tp.server.bases.Resource import Resource

from tp.server.rules.dronesec.objects.Fleet import Fleet

class ProduceDrones(Order):
	"""\
Build a new drone."""
	typeno = 2
	attributes = {\
		'ships': Order.Attribute("ships", {}, 'protected', type=netlib.objects.constants.ARG_LIST,
					desc="Build Drones."),
		'name':  Order.Attribute("name", 'New Drones', 'protected', type=netlib.objects.constants.ARG_STRING,
					desc="The new drone's name.")
	}


	def do(self):
		builder = Object(self.oid)

		if not hasattr(builder, "owner"):
			print "Could not do a build order because it was on an unownable object."
			self.remove()

		#Check to see if there enough resources
		res = 0
		for type, number in self.ships.items():
			res += int(Fleet.DP.cost[type]) * int(number)

		print res
		if res > builder.resources[1][0]:
			print "Not enough resources"
			self.remove()

		if self.turns() > 1:
			# Add another year to worked...
			self.worked += 1
			print "Worked %s, %s left until built." % (self.worked, self.turns())
			self.save()
			return

		# Build new fleet object
		fleet = Object(type='tp.server.rules.dronesec.objects.Fleet')

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
				message.body += "%s %ss" % (number, Fleet.DP.name[type])
			else:
				message.body += "%s %s" % (number, Fleet.DP.name[type])

		message.insert()

		#Remove resources for unit
		builder.resources_add(Resource.byname('Credit'), -res)
		builder.save()

		self.remove()

	def turns(self, turns=0):
		for type, number in self.ships.items():
			turns += 0 * number

		return turns-self.worked

	def resources(self):
		res = 0
		for type, number in self.ships.items():
			res += int(Fleet.DP.cost[type]) * int(number)
		r = Resource.byname('Credit')
		return [(r,res),]

	def fn_ships(self, value=None):
		print value
		if value == None:
			returns = []
			for type, name in Fleet.DP.name.items():
				returns.append((type, name, 10))
			return returns, self.ships.items()
		else:
			ships = {}

			try:
				for type, number in value[1]:
					if not type in Fleet.DP.name.keys():
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
