#This class will hold the Drones a player can guild

class DroneAvailability:
	def __init__(self, game):
		self.players = {}
		self.game = game

	def addPlayer(self, id):
		import tp.server.rules.dronesec.master
		Jarvis = tp.server.rules.dronesec.master.Controller()
		self.DP = Jarvis.DP[self.game]
		self.PL = Jarvis.PL[self.game]
		self.ML = Jarvis.ML[self.game]
		if not self.players.has_key(id):
			self.players[id] = dict()
			self.buildList(id)
		else:
			print "Player already Added"

	def buildList(self, playerId):
		for id, ship in self.DP.name.items():
			if len(self.DP.requirements[id]) == 0:
				self.players[playerId][id] = ship

	def addDrone(self, playerID, drone):
		if not self.players[playerID].has_key(drone):
			if ML.masterNames[DP.requirements[drone]] in self.PL.players[playerID]:
				self.players[playerId][drone] = self.DP.name[drone]

