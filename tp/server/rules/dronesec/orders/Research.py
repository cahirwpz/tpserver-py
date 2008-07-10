
from tp import netlib

from tp.server.bases.Object import Object
from tp.server.bases.Order import Order
from tp.server.bases.Message import Message
from tp.server.bases.Resource import Resource
from tp.server.rules.dronesec.bases.Player import Player
from tp.server.rules.dronesec.bases.Research import Research as Res
from tp.server.rules.dronesec.bases.Drone import Drone

class Research(Order):
	"""\
Build a new drone."""
	typeno = 105
	attributes = {\
		'research': Order.Attribute("research", {}, 'protected', type=netlib.objects.constants.ARG_LIST,
					desc="Research Upgrades."),
	}


	def do(self):
		researcher = Object(self.oid)

		if not hasattr(researcher, "owner"):
			print "Could not do a build order because it was on an unownable object."
			self.remove()

		message = Message()
		message.slot = -1
		message.bid = researcher.owner

		res = researcher.resources[1][0]
		player = Player(researcher.owner)
		resLeft = res
		totalUsed = 0
		for id in self.research.keys():
			if resLeft == 0:
				break
			if not player.canResearch.has_key(id):
				continue
			res = resLeft
			resRatio = 1
			researches = Res.bytype('tp.server.rules.dronesec.research.EconomyType')
			resList = []
			for x in Player(researcher.owner).research:
				if x in researches:
					resList.append(x)
			researches = resList
			if researches:
				for i in researches:
					if Res(id).type.endswith(Res(i).researchType) or 'All' in Res(i).researchType:
						resRatio += Res(i).researchRatio


			finished, resLeft = player.researchQuota(id, res, resRatio)
			
			totalUsed += res - resLeft
			print totalUsed
			if finished:
				player.addResearch(id)

				if Res(id).type.endswith('UnitType'):
					drone = Drone.byname(Res(id).ship)
					player.addDrone(drone)

				print "Research %s finished at %s" % (self.research[id], researcher.name)

				message.subject = "Research Complete"

				message.body = """\
Your scientists have discovered new a new technology!
You have discovered %s at %s
""" % (Res(id).name, researcher.name)
				message.insert()
				del self.research[id]

		if len(self.research) == 0:
			self.remove()
		#Remove resources for unit
		researcher.resources_add(Resource.byname('Credit'), -totalUsed)
		researcher.save()
		player.save()


	def turns(self, turns=0):
		builder = Object(self.oid)
		for type in self.research.keys():
			if Player(builder.owner).researchLeft.has_key(type):
				turns += 1 + ((Res(type).cost -
					(builder.resources[1][0]) + Player(builder.owner).researchLeft[type]) / 100)
			else:
				turns += 1  + (Res(type).cost - builder.resources[1][0]) / 100

		return turns-self.worked

	def resources(self):
		return []

	def fn_research(self, value=None):
		builder = Object(self.oid)
		if value == None:
			returns = []
			for type, name in Player(builder.owner).canResearch.items():
				returns.append((type, name, 1))
			return returns, self.research.items()
		else:
			research = {}

			try:
				for type, number in value[1]:
					if not type in Player(builder.owner).canResearch.keys():
						raise ValueError("Invalid type selected")
					research[type] = number
			except:
				pass

			self.research = research