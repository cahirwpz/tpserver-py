
from tp import netlib

from tp.server.bases.Object import Object
from tp.server.bases.Order import Order
from tp.server.bases.Message import Message
from tp.server.bases.Resource import Resource
from tp.server.rules.dronesec.objects.Fleet import Fleet

from tp.server.rules.dronesec.bases.Player import Player
from tp.server.rules.dronesec.bases.Drone import Drone
from tp.server.rules.dronesec.research.ResearchCalculator import ResearchCalculator as RC

class ProduceDrones(Order):
	"""\
Build a new drone."""
	typeno = 102
	attributes = {\
		'ships': Order.Attribute("ships", {}, 'protected', type=netlib.objects.constants.ARG_LIST,
					desc="Build Drones."),
		'wait': Order.Attribute("wait", 0, 'protected', type= netlib.objects.constants.ARG_TIME,
					desc="Length of Time until this order ends."),
	}


	def do(self):
		builder = Object(self.oid)

		if not hasattr(builder, "owner"):
			print "Could not do a build order because it was on an unownable object."
			self.remove()

		for type in self.ships.keys():
			#Check to see if there enough resources

			res = 0
			no = 0
			cost, costRatio = RC.EconomyDrone(builder.owner, type)
			no =  int(builder.resources[1][0] / (cost * costRatio))
			res = int(no * cost * costRatio)

			message = Message()
			message.slot = -1
			message.bid = builder.owner

			#In Theory: This should never be true.
			if res > builder.resources[1][0]:
				print "Not enough resources"
				message.subject = "Not enough resources"
				message.body = """Drone production at %s halted due to insufficient resources.
Had %s and needed %s""" % (buider.name, builder.resources[1][0], res)
				return


			# If player gives a length above 1 the order produce drones until
			# the length is 1
			# If the player gives a length 0 or less then the order will
			# continue producing until changed

			# Build new fleet object
			fleet = Object(type='tp.server.rules.dronesec.objects.Fleet')

			# Type Fleet
			fleet.parent = builder.id
			fleet.posx = builder.posx
			fleet.posy = builder.posy
			fleet.posz = builder.posz
			fleet.size = 1
			fleet.owner = builder.owner
			fleet.ships = {type : no}
			fleet.insert()
			fleet.name = ("%s Fleet" % (Drone(type).name)).strip()
			fleet.save()
			print "Drone fleet produced at %s using %s resources" % (builder.id, res)

			message.subject = "Drone built"

			message.body = """\
A new fleet (%s) has been built and is orbiting %s.
It consists of:
""" % (fleet.name, builder.name)
			for type, number in fleet.ships.items():
				if number > 1:
					message.body += "%s %ss" % (number, Drone(type).name)
				else:
					message.body += "%s %s" % (number, Drone(type).name)

			message.insert()

			#Remove resources for unit
			builder.resources_add(Resource.byname('Credit'), -res)
			builder.save()
			
			
			#Removes order if length was given (not zero) and after drones are produced
			if self.wait == 1:
				self.remove()
			elif self.wait > 1:
				# Lower the length
				self.wait -= 1
				self.save()

	def turns(self, turns=0):
		return turns + self.wait

	def resources(self):
		return []
##		res = 0
##		for type, number in self.ships.items():
##			res += Drone(type).cost * int(number)
##		r = Resource.byname('Credit')
##		return [(r,res),]

	def fn_ships(self, value=None):
		builder = Object(self.oid)
		if value == None:
			returns = []
			for type, name in Player(builder.owner).drones.items():
				returns.append((type, name, 1))
			return returns, self.ships.items()
		else:
			ships = {}

			try:
				for type, number in value[1]:
					if not type in Player(builder.owner).drones.keys():
						raise ValueError("Invalid type selected")
					ships[type] = number
					break
			except:
				pass

			self.ships = ships

	def fn_wait(self, value=None):
		if value is None:
			return self.wait, -1
		else:
			self.wait = value[0]