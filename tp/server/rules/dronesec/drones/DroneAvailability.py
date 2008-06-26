#This class will hold the Drones a player can guild

class DroneAvailability:
	def __init__(self, game):
		self.players = {}
		self.game = game

	def addPlayer(self, id):
		if not self.players.has_key(id):
			self.players[id] = dict()
			self.buildList(id)
		else:
			print "Player already Added"

	def buildList(self, playerId):
		import tp.server.rules.dronesec.master
		Jarvis = tp.server.rules.dronesec.master.Controller()
		DP = Jarvis.DP[self.game]
		for id, ship in DP.name.items():
			if len(DP.requirements[id]) == 0:
				self.players[playerId][id] = ship

	def addDrone(self, playerID, drone):
		import tp.server.rules.dronesec.master
		Jarvis = tp.server.rules.dronesec.master.Controller()
		DP = Jarvis.DP[self.game]
		PL = Jarvis.PL[self.game]
		ML = Jarvis.ML[self.game]
		if not self.players[playerID].has_key(drone):
			for req in DP.requirements[drone]:
				reqList = ML.masterNames[req]
			if reqList in PL.players[playerID]:
				self.players[playerID][drone] = DP.name[drone]

