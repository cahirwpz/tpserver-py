#Master list  holds all of the researches available and determines their availability

from tp.server.rules.dronesec.bases.Research import Research
##from CombatType import CombatType
from UnitType import UnitType
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
				print r.type
				r.ship = ship
				r.insert()

