#Master list  holds all of the researches available and determines their availability

from Research import Research
from ResearchType import ResearchType
from CombatType import CombatType
from UnitType import UnitType
import csv
import os

class MasterList:
	def __init__(self):
		#Load all types
		self.master = {}
		self.masterNames = {}
##		self.combatTypes = self.loadType(f = "combat.csv")
##		self.economyTypes = self.loadType(f = "economy.csv")
##		self.worldTypes = self.loadType(f = "world.csv")
		self.unitTypes = self.loadUnitType(f = "units.csv")


	def loadUnitType(self, f):
		# """load and return a list of researchs of this type
		#    f is the file to be loaded as the holder of information"""
		try:
			reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/research/"),f)))
		except:
			reader = csv.reader(open(f))

		resIds = {}
		resNames = {}
		researches = {}
		self.ids = []

		for name, abbrev, cost, requirements, ship in reader:
			if name != 'Name':
				i = self.getId()
				reqs = requirements.strip().split()
				res = UnitType(i, name, abbrev, cost, reqs)
				res.ship = ship
				resIds[i] = name
				resNames[name] = i
				researches[i] = res
				self.master[i] = res
				self.masterNames[name] = i

		return ResearchType(resIds, resNames, researches)

	def loadType(self, f):
		# """load and return a list of researchs of this type
		#    f is the file to be loaded as the holder of information"""
		try:
			reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/research/"),f)))
		except:
			reader = csv.reader(open(f))

		resIds = {}
		resNames = {}
		researches = {}
		self.ids = []

		for name, abbrev, cost, requirements in reader:
			if name != 'Name':
				i = self.getId()
				reqs = requirements.strip().split()
				res = Research(i, name, abbrev, cost, reqs)
				resIds[i] = name
				resNames[abbrev] = i
				researches[i] = res
				self.master[i] = res
				self.masterNames[name] = i

		return ResearchType(resIds, resNames, researches)

	def getId(self):
	#Possibility: Make IDS random
		try:
			i = len(self.ids)
		except:
			i = 0
		self.ids.append(i)
		return i
