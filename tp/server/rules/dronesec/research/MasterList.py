#Master list  holds all of the researches available and determines their availability

from tp.server.rules.dronesec.bases.Research import Research

from tp.server.bases.Design import Design
from tp.server.bases.Component import Component
from tp.server.bases.Category import Category

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
				
				
				# A Design is created for each Research for user-friendliness
				d = Design()
				d.name  = name
				d.id = 200 + r.id
				d.desc  = ""
				d.owner = -1
				d.categories = [Category.byname('Research - World Researches')]
				d.components = []
				d.components.append((Component.byname('Cost'), cost))
				d.components.append((Component.byname('Speed Ratio(%)'),   int(r.speedRatio*100)))
				d.components.append((Component.byname('Power'),   power))
				d.insert()
				
				
			else:
				# Components are defined the first time based on the names of the columns
				for x in (cost, speed, speedRatio, power):
					try:
						Component.byname(x)
					except:
						c = Component()
						c.categories = [Category.byname('Research')]
						if x.endswith('Ratio'):
							x = x + '(%)'
						c.name = x
						c.desc = ""
						c.properties  = {}
						c.insert()

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
				
				
				# A Design is created for each Researchfor user-friendliness
				d = Design()
				d.name  = name
				d.id = 200 + r.id
				d.desc  = ""
				d.owner = -1
				d.categories = [Category.byname('Research - Economy Researches')]
				d.components = []
				d.components.append((Component.byname('Cost'), cost))
				d.components.append((Component.byname('Resource'), resources))
				d.components.append((Component.byname('Resource Ratio(%)'),      int(r.resourceRatio*100)))
				d.components.append((Component.byname('Research Ratio(%)'),   int(r.researchRatio*100)))
				d.components.append((Component.byname('Drone Cost'),   droneCost))
				d.components.append((Component.byname('Drone Cost Ratio(%)'),   int(r.droneRatio*100)))
				d.insert()
				
			else:
				# Components are defined the first time based on the names of the columns
				for x in (resources, resourceRatio, researchRatio, droneCost, droneRatio):
					try:
						Component.byname(x)
					except:
						c = Component()
						c.categories = [Category.byname('Research')]
						if x.endswith('Ratio'):
							x = x + '(%)'
						c.name = x
						c.desc = ""
						c.properties  = {}
						c.insert()

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
				r.ships = ships.strip()
				r.types = types.strip().split(',')
				r.insert()
				
				
				# A Design is created for each Research for user-friendliness
				d = Design()
				d.name  = name
				d.id = 200 + r.id
				d.desc  = ""
				d.owner = -1
				d.categories = [Category.byname('Research - Combat Researches')]
				d.components = []
				d.components.append((Component.byname('Cost'), cost))
				d.components.append((Component.byname('Damage'),      damage))
				d.components.append((Component.byname('Number of Attacks'),   numAttacks))
				d.components.append((Component.byname('Health'),   health))
				d.insert()
				
				
			else:
				# Components are defined the first time based on the names of the columns
				for x in (cost, damage, numAttacks, health):
					try:
						Component.byname(x)
					except:
						c = Component()
						c.categories = [Category.byname('Research')]
						c.name = x
						c.desc = ""
						c.properties  = {}
						c.insert()

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
					ct = Research(CombatType.byname(abbrev))
					damage, numAttacks, health = int(damage), int(numAttacks), int(health)
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

		for id in CombatType.bytype('tp.sever.rules.dronesec.research.CombatType'):
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
					r = Research(id = Research.byname(abbrev))
					speed, speedRatio, power = int(speed), int(speedRatio), int(power)
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

		for id in WorldType.bytype('tp.sever.rules.dronesec.research.WorldType'):
			if id not in researches:
				r = Research(id)
				print 'A research %s has been removed' % r.name
				r.remove()

	@classmethod
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
					resources, resourceRatio, researchRatio, droneCost, droneRatio = int(resources), int(resourceRatio), int(ResearchRatio), int(droneCost), int(droneRatio)
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

		for id in EconomyType.bytype('tp.sever.rules.dronesec.research.EconomyType'):
			if id not in researches:
				r = Research(id)
				print 'A research %s has been removed' % r.name
				r.remove()