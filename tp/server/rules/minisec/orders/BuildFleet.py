
import netlib

from sbases.Object import Object
from sbases.Order import Order
from sbases.Message import Message

from sobjects.Fleet import Fleet

class BuildFleet(Order):
	"""\
Build a new star ship fleet."""

	attributes = {\
		'ships': Order.Attribute("ships", {}, 'protected', type=netlib.objects.constants.ARG_LIST, 
				desc="Ships to build and launch.")
	}
	
	def do(self):
		builder = Object(self.oid)

		if not hasattr(builder, "owner"):
			print "Could not do a build order because it was on an unownable object."
			self.remove()
		
		if self.turns() != 0:
			# Add another year to worked...
			self.worked += 1
			self.save()
			return
			
		# Build new fleet object
		fleet = Object(type='sobjects.Fleet')

		# Type Fleet
		fleet.name = "New fleet"
		fleet.parent = builder.parent
		fleet.posx = builder.posx
		fleet.posy = builder.posy
		fleet.posz = builder.posz
		fleet.velx = 0
		fleet.vely = 0
		fleet.velz = 0
		fleet.size = 1
		fleet.owner = builder.owner
		fleet.ships = self.ships
		fleet.save()

		message = Message()
		message.slot = 0
		message.bid = builder.owner
		message.subject = "Fleet built"
		
		message.body = """\
A new fleet has been built and is orbiting %s.
It consists of:
""" % builder.name

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

BuildFleet.typeno = 2
Order.types[BuildFleet.typeno] = BuildFleet
