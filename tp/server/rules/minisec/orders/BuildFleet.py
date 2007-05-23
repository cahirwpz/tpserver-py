
from tp import netlib

from tp.server.bases.Object import Object
from tp.server.bases.Order import Order
from tp.server.bases.Message import Message

from tp.server.rules.minisec.objects.Fleet import Fleet

class BuildFleet(Order):
	"""\
Build a new star ship fleet."""
	typeno = 2

	attributes = {\
		'ships': Order.Attribute("ships", {}, 'protected', type=netlib.objects.constants.ARG_LIST, 
					desc="Ships to build and launch."),
		'name':  Order.Attribute("name", 'New Fleet', 'protected', type=netlib.objects.constants.ARG_STRING, 
					desc="The new fleet's name.")
	}
	
	def do(self):
		builder = Object(self.oid)

		if not hasattr(builder, "owner"):
			print "Could not do a build order because it was on an unownable object."
			self.remove()
		
		if self.turns() > 1:
			# Add another year to worked...
			self.worked += 1
			self.save()
			return
			
		# Build new fleet object
		fleet = Object(type='tp.server.rules.minisec.objects.Fleet')

		# Type Fleet
		fleet.parent = builder.id
		fleet.posx = builder.posx
		fleet.posy = builder.posy
		fleet.posz = builder.posz
		fleet.size = 1
		fleet.owner = builder.owner
		fleet.ships = self.ships
		fleet.insert()
		fleet.name = "Fleet %i" % fleet.id
		fleet.save()

		message = Message()
		message.slot = -1
		message.bid = builder.owner
		message.subject = "Fleet built"
		
		message.body = """\
A new fleet (%s) has been built and is orbiting %s.
It consists of:
""" % (fleet.name, builder.name)

		for type, number in fleet.ships.items():
			if number > 1:
				message.body += "%s %ss" % (number, Fleet.ship_types[type])
			else:
				message.body += "%s %s" % (number, Fleet.ship_types[type])

		message.insert()

		self.remove()

	def turns(self, turns=0):
		time = {0:1, 1:2, 2:4}
	
		for type, number in self.ships.items():
			turns += time[type] * number

		return turns-self.worked

	def resources(self):
		return []

	def fn_ships(self, value=None):
		if value == None:
			returns = []
			for type, name in Fleet.ship_types.items():
				returns.append((type, name, -1))
			return returns, self.ships.items()
		else:
			ships = {}

			try:
				for type, number in value[1]:
					if not type in Fleet.ship_types.keys():
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

