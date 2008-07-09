#Master list  holds all of the researches available and determines their availability

from tp.server.rules.dronesec.bases.Research import Research
from CombatType import CombatType
from UnitType import UnitType
from WorldType import WorldType
from EconomyType import EconomyType
import csv
import os

class MasterList:
	@classmethod
	def loadUnitType(cls, f = "units.csv"):
		# """load and return a list of researchs of this type
		#    f is the file to be loaded as the holder of information"""
		try:
			reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/research/"),f)))
		except:
			reader = csv.reader(open(f))

		for name, abbrev, cost, requirements, ship in reader:
			if name != 'Name':
				r = UnitType()
				r.name = name
				r.abbrev = abbrev
				r.cost = cost
				r.reqs = requirements.strip().split()
				r.ship = ship
				r.insert()

	@classmethod
	def loadWorldType(cls, f = "world.csv"):
		# """load and return a list of researchs of this type
		#    f is the file to be loaded as the holder of information"""
		try:
			reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/research/"),f)))
		except:
			reader = csv.reader(open(f))

		for name, abbrev, cost, requirements, speed, speedRatio, power, units, types in reader:
			if name != 'Name':
				r = WorldType()
				r.name = name
				r.abbrev = abbrev
				r.cost = cost
				r.reqs = requirements.strip().split()
				r.speed = int(speed)
				r.speedRatio = float(speedRatio)
				r.power = int(power)
				r.units = units.strip().split(',')
				r.types = types.strip().split(',')
				r.insert()

	@classmethod
	def loadEconomyType(cls, f = "economy.csv"):
		# """load and return a list of researchs of this type
		#    f is the file to be loaded as the holder of information"""
		try:
			reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/research/"),f)))
		except:
			reader = csv.reader(open(f))

		for name, abbrev, cost, requirements, resources, resourceRatio, researchRatio, researchType in reader:
			if name != 'Name':
				r = EconomyType()
				r.name = name
				r.abbrev = abbrev
				r.cost = cost
				r.reqs = requirements.strip().split()
				r.resources = int(resources)
				r.resourceRatio = float(resourceRatio)
				r.researchRatio = float(researchRatio)
				r.researchType = researchType.strip().split(',')
				r.insert()


	@classmethod
	def loadCombatType(cls, f = "combat.csv"):
		# """load and return a list of researchs of this type
		#    f is the file to be loaded as the holder of information"""
		try:
			reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/research/"),f)))
		except:
			reader = csv.reader(open(f))

		for name, abbrev, cost, requirements, damage, numAttacks, health, types, ships in reader:
			if name != 'Name':
				r = CombatType()
				r.name = name
				r.abbrev = abbrev
				r.cost = cost
				r.reqs = requirements.strip().split()
				r.damage = int(damage)
				r.numAttacks = int(numAttacks)
				r.health = int(health)
				r.ships = ships.strip().split(',')
				r.types = types.strip().split(',')
				r.insert()