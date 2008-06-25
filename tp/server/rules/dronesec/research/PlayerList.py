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


	def addResearch(self, id, research):
		if research not in self.players[id]:
			self.players[id].append(research)


	def researchQuota(self, id, research, payed):
		if research not in self.researchLeft[id]:
			self.researchLeft[id][research] = 0

		self.researchLeft[id][research] += payed

	def buildList(self, id):
		import tp.server.rules.dronesec.master
		Jarvis = tp.server.rules.dronesec.master.Controller()
		ML = Jarvis.ML[self.game]
		for res, type in ML.items():
			if res not in players[id]:
				canResearch = {}