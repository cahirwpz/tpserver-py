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
		self.attack = dict()
		self.health = dict()
		self.speed= dict()
		self.stength= dict()
		self.weakness = dict()
		for name, typ, cost, attack, health, speed, strength, weakness in reader:
			##hack: It should be checking for the column headers not for id. (In case we use random values instead of sequential ones.
			if name != 'Name':
				i = self.getId()
				self.id[name] = i
				self.name[i]= name
				self.type[i] = typ
				self.cost[i] = cost
				self.attack[i] = attack
				self.health[i] = health
				self.speed[i]= speed
				self.stength[i]= strength
				self.weakness[i] = weakness

	def getId(self):
	#Possibility: Make IDS randomla
		try:
			i = len(self.ids)
		except:
			i = 0
		self.ids.append(i)
		return i