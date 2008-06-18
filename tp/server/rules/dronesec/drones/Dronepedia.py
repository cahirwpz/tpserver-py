#Dronepedia holds the information of all the drones in a cross-referencionable library.

import csv
import os

class Dronepedia:
	def __init__(self, f = "drones.csv"):
		# """Initialize dronepedia.
		#    f is the file to be loaded as the holder of information"""
		try:
			reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/drones"),f)))
		except:
			reader = csv.reader(open(f))
		self.ids = []
		self.id = dict()
		self.name= dict()
		self.type = dict()
		self.cost = dict()
		self.power = dict()
		self.attack = dict()
		self.numAttacks = dict()
		self.health = dict()
		self.speed= dict()
		self.strength= dict()
		self.weakness = dict()
		for name, typ, cost, power, attack, numAttacks, health, speed, strength, weakness in reader:
			if name != 'Name':
				i = self.getId()
				self.id[name] = i
				self.name[i]= name
				self.type[i] = typ
				self.cost[i] = int(cost)
				self.power[i] = int(power)
				self.attack[i] = int (attack)
				self.numAttacks[i] = int(numAttacks)
				self.health[i] = int(health)
				self.speed[i]= int(speed)
				self.strength[i]= strength
				self.weakness[i] = weakness

	def getId(self):
	#Possibility: Make IDS randomla
		try:
			i = len(self.ids)
		except:
			i = 0
		self.ids.append(i)
		return i