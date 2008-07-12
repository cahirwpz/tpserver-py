
from tp.server.rules.dronesec.bases.Research import Research
from tp.server.rules.dronesec.bases.Player import Player
from tp.server.rules.dronesec.bases.Drone import Drone


class ResearchCalculator:
	@classmethod
	def Economy(self, owner, type = None):
		resources = 0
		resourceRatio = 1
		researchRatio = 1
		researches = Research.bytype('tp.server.rules.dronesec.research.EconomyType')
		res = []
		for x in Player(owner).research:
			if x in researches:
				res.append(x)
		researches = res
		if researches:
			for id in researches:
				resources += Research(id).resources
				resourceRatio += Research(id).resourcesRatio
				if type != None:
					if type in Research(id).researchType or 'All' in Research(id).researchType:
						researchRatio += Research(id).researchRatio
		
		return resources, resourceRatio, researchRatio
	

	@classmethod
	def EconomyDrone(self, owner, drone):
		cost = Drone(drone).cost
		costRatio = 1
		researches = Research.bytype('tp.server.rules.dronesec.research.EconomyType')
		res = []
		for x in Player(owner).research:
			if x in researches:
				res.append(x)
		researches = res
		if researches:
			for id in researches:
				if Drone(drone).type in Research(id).droneTypes or Drone(drone).name in Research(id).droneShips or 'All' in Research(id).droneTypes or 'All' in Research(id).droneShips:
					cost -= Research(id).droneCost
					costRatio -= Research(id).droneRatio
		return cost, costRatio

	@classmethod
	def World(self, owner, drone):

		power = Drone(drone).power
		speed = Drone(drone).speed
		speedRatio = 1
		researches = Research.bytype('tp.server.rules.dronesec.research.WorldType')
		res = []
		for x in Player(owner).research:
			if x in researches:
				res.append(x)
		researches = res
		if researches:
			for id in researches:
				if Drone(drone).type in Research(id).types or Drone(drone).name in Research(id).units:
					power += Research(id).power
					speed += Research(id).speed
					speedRatio += Research(id).speedRatio
		
		return power, speed, speedRatio

	@classmethod
	def Combat(self, owner, drone):

		damage = Drone(drone).attack
		numAttacks = Drone(drone).numAttacks
		health = Drone(drone).health
		researches = Research.bytype('tp.server.rules.dronesec.research.CombatType')
		res = []
		for x in Player(owner).research:
			if x in researches:
				res.append(x)
		researches = res
		if researches:
			for id in researches:
				if Drone(drone).type in Research(id).types or Drone(drone).name in Research(id).ships or 'All' in Research(id).types:
					numAttacks += Research(id).numAttacks
					damage += Research(id).damage
					health += Research(id).health

		return damage, numAttacks, health
