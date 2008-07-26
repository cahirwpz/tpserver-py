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
		for name, abbrev, cost, requirements, resources, resourceRatio, researchRatio, researchType, droneCost, droneRatio, droneTypes, droneShips in reader:
			if name != 'Name':
				r = EconomyType()
				r.name = name
				r.abbrev = abbrev
				r.cost = cost
				r.reqs = requirements.strip().split()
				r.resources = int(resources)
				r.resourceRatio = float(resourceRatio)
				r.researchRatio = float(researchRatio)
				r.researchType = researchType.strip()
				r.droneCost = int(droneCost)
				r.droneRatio = float(droneRatio)
				r.droneTypes = droneTypes.strip().split(',')
				r.droneShips = droneShips.strip().split(',')
				r.insert()


	@classmethod
	def loadCombatType(cls, f = "combat.csv"):
		# """load and return a list of researchs of this type
		#    f is the file to be loaded as the holder of information"""
		try:
			reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/research/"),f)))
		except:
			reader = csv.reader(open(f))
		for name, abbrev, cost, requirements, damage, numAttacks, health, strength, weakness, types, ships in reader:
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

	@classmethod
	def syncCombatType(cls, f = 'combat.csv'):
		try:
			reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/research/"),f)))
		except:
			reader = csv.reader(open(f))
			
		researches = []
		for name, abbrev, cost, requirements, damage, numAttacks, health, strength, weakness, types, ships in reader:
			if name != 'Name':
				try:
					ct = CombatType(CombatType.byname(abbrev))
					if ct.damage != damage or ct.numAttacks != numAttacks or ct.health != health:
						ct.damage = damage
						ct.numAttacks = numAttacks
						ct.health = health
						print "The Research '%s' has been modified" % ct.name
						ct.save()
					researches.append(ct.id)
				except:
					#Add research
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
					researches.append(r.id)
					'A research %s has been added' % name

		for id,time in CombatType.ids():
			if id not in researches:
				r = Research(id)
				print 'A research %s has been removed' % r.name
				r.remove()

	@classmethod
	def syncWorldType(cls, f = 'world.csv'):
		try:
			reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/research/"),f)))
		except:
			reader = csv.reader(open(f))
			
		researches = []
		for name, abbrev, cost, requirements, speed, speedRatio, power, units, types in reader:
			if name != 'Name':
				try:
					r = WorldType(WorldType.byname(abbrev))
					if r.speed != speed or r.speedRatio != speedRatio or r.power != power:
						r.speed = speed
						r.speedRatio = speedRatio
						r.power = power
						print "The Research '%s' has been modified" % r.name
						r.save()
					researches.append(r.id)
				except:
					#Add research
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
					researches.append(r.id)
					'A research %s has been added' % name

		for id,time in WorldType.ids():
			if id not in researches:
				r = Research(id)
				print 'A research %s has been removed' % r.name
				r.remove()

def syncEconomyType(cls, f = 'economy.csv'):
		try:
			reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/research/"),f)))
		except:
			reader = csv.reader(open(f))
			
		researches = []
		for name, abbrev, cost, requirements, resources, resourceRatio, researchRatio, researchType, droneCost, droneRatio, droneTypes, droneShips in reader:
			if name != 'Name':
				try:
					r = EconomyType(EconomyType.byname(abbrev))
					if r.resources != resources or r.resourceRatio != resourceRatio or r.researchRatio != researchRatio or r.droneCost != droneCost or r.droneRatio != droneRatio:
						r.resources = resources
						r.resourceRatio = resourceRatio
						r.researchRatio = researchRatio
						r.droneCost = droneCost
						r.droneRatio = droneRatio
						print "The Research '%s' has been modified" % r.name
						r.save()
					researches.append(r.id)
				except:
					#Add research
					r = EconomyType()
					r.name = name
					r.abbrev = abbrev
					r.cost = cost
					r.reqs = requirements.strip().split()
					r.resources = int(resources)
					r.resourceRatio = float(resourceRatio)
					r.researchRatio = float(researchRatio)
					r.researchType = researchType.strip()
					r.droneCost = int(droneCost)
					r.droneRatio = float(droneRatio)
					r.droneTypes = droneTypes.strip().split(',')
					r.droneShips = droneShips.strip().split(',')
					r.insert()
					researches.append(r.id)
					'A research %s has been added' % name

		for id,time in EconomyType.ids():
			if id not in researches:
				r = Research(id)
				print 'A research %s has been removed' % r.name
				r.remove()