#This class will hold the list of upgrades researched to players.

class PlayerList:
	def __init__(self, game):
		self.players = {}
		self.researchLeft = {}
		self.canResearch = {}
		self.game = game

	def addPlayer(self, id):
		if not self.players.has_key(id):
			self.players[id] = []
		if not self.researchLeft.has_key(id):
			self.researchLeft[id] = {}
		if not self.canResearch.has_key(id):
			self.canResearch[id] = {}
			self.buildList(id)


	def addResearch(self, id, research):
		if research not in self.players[id]:
			self.players[id].append(research)
		if research in self.researchLeft.keys():
			del self.researchLeft[id][research]
		if research in self.canResearch[id]:
			print self.canResearch
			del self.canResearch[id][research]
			print self.canResearch


	def researchQuota(self, id, research, payed):
		if research not in self.researchLeft[id]:
			self.researchLeft[id][research] = 0
		self.researchLeft[id][research] += payed

		import tp.server.rules.dronesec.master
		Jarvis = tp.server.rules.dronesec.master.Controller()
		ML = Jarvis.ML[self.game]
		if self.researchLeft[id][research] >= ML.master[research].cost:
			return True, self.researchLeft[id][research] - ML.master[research].cost
		else: return False, 0


	def buildList(self, id):
		import tp.server.rules.dronesec.master
		Jarvis = tp.server.rules.dronesec.master.Controller()
		ML = Jarvis.ML[self.game]
		for res, type in ML.master.items():
			if res not in self.players[id]:
				reqList = []
				if len(ML.master[res].requirements) > 1:
					for req in ML.master[res].requirements:
						reqList.append(ML.masterNames[req])
				elif len(ML.master[res].requirements) == 1:
					reqList = ML.master[res].requirements[0]
				else:
					self.canResearch[id][res] = type.name
				if reqList in self.players[id]:
					self.canResearch[id][res] = type.name