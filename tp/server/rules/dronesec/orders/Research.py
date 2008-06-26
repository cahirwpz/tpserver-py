
from tp import netlib

from tp.server.bases.Object import Object
from tp.server.bases.Order import Order
from tp.server.bases.Message import Message
from tp.server.bases.Resource import Resource

import tp.server.rules.dronesec.master

class Research(Order):
	"""\
Build a new drone."""
	typeno = 5
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


		Jarvis = tp.server.rules.dronesec.master.Controller()
		resLeft = res
		totalUsed = 0
		for id in self.research.keys():
			if resLeft == 0:
				break
			if not Jarvis.PL[researcher.game].canResearch[researcher.owner].has_key(id):
				continue
			res = resLeft
			finished, resLeft = Jarvis.PL[researcher.game].researchQuota(researcher.owner, id, resLeft)
			totalUsed += res - resLeft
			if finished:
				Jarvis.PL[researcher.game].addResearch(researcher.owner, id)
				Jarvis.save()

				if id in Jarvis.ML[researcher.game].unitTypes.ids:
					drone = Jarvis.DP[researcher.game].id[Jarvis.ML[researcher.game].master[id].ship]
					Jarvis.DA[researcher.game].addDrone(researcher.owner, drone)

				print "Research %s finished at %s" % (self.research[id], researcher.name)

				message.subject = "Research Complete"

				message.body = """\
Your scientists have discovered new a new technology!
You have discovered %s at %s
""" % (self.research[id], researcher.name)
				message.insert()
				del self.research[id]

		Jarvis.PL[researcher.game].buildList(researcher.owner)
		if len(self.research) == 0:
			self.remove()
		#Remove resources for unit
		researcher.resources_add(Resource.byname('Credit'), -totalUsed)
		researcher.save()
		Jarvis.save()


	def turns(self, turns=0):
		builder = Object(self.oid)
		Jarvis = tp.server.rules.dronesec.master.Controller()
		for type in self.research.keys():
			turns += 1 + int((Jarvis.ML[builder.game].master[type].cost -
				(builder.resources[1][0]) + Jarvis.PL[builder.game].researchLeft[type]) / 100)

		return turns-self.worked

	def resources(self):
		return []

	def fn_research(self, value=None):
		builder = Object(self.oid)
		Jarvis = tp.server.rules.dronesec.master.Controller()
		if value == None:
			returns = []
			for type, name in Jarvis.PL[builder.game].canResearch[builder.owner].items():
				returns.append((type, name, 1))
			return returns, self.research.items()
		else:
			research = {}

			try:
				for type, number in value[1]:
					if not type in Jarvis.ML[builder.game].master.keys():
						raise ValueError("Invalid type selected")
					research[type] = number
			except:
				pass

			self.research = research