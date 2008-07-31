#Dronepedia loads the Drones to the database for a game.

import csv
import os
from tp.server.bases.Component import Component
from tp.server.rules.dronesec.bases.Drone import Drone
from tp.server.bases.Category import Category
from tp.server.bases.Design import Design


class Dronepedia:
	def __init__(self, f = "drones.csv"):
		"""
		\Initialize dronepedia.
		f is the file to be loaded as the holder of information"""
		try:
			reader = csv.reader(open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/drones"),f)))
		except:
			reader = csv.reader(open(f))
		for name, typ, cost, power, attack, numAttacks, health, speed, strength, weakness, requirements in reader:
			if name != 'Name':

				drone = Drone()
				drone.name = name
				drone.type = typ
				drone.cost = int(cost)
				drone.power = int(power)
				drone.attack = int(attack)
				drone.numAttacks = int(numAttacks)
				drone.health = int(health)
				drone.speed = int(speed)
				drone.strength = strength
				drone.weakness = weakness
				drone.reqs = requirements
				drone.insert()
				
				
				d = Design()
				d.name  = name
				d.id = drone.id
				d.desc  = ""
				d.owner = -1
				d.categories = [Category.byname(typ)]
				d.components = []
				d.components.append((Component.byname('Cost'), cost))
				d.components.append((Component.byname('Power'),      power))
				d.components.append((Component.byname('Attack'),   attack))
				d.components.append((Component.byname('Number of Attacks'),   numAttacks))
				d.components.append((Component.byname('Health'),   health))
				d.components.append((Component.byname('Speed'),   speed))
##				d.components.append((Component.byname('Strength'),   strength))
##				d.components.append((Component.byname('Weakness'),   weakness))
##				d.components.append((Component.byname('Requirements'),   requirements))
				d.insert()
				
			else:
				for x in (typ, cost, power, attack, numAttacks, health, speed, strength, weakness, requirements):
					c = Component()
					c.categories = [Category.byname('Drones')]
					c.name = x
					c.desc = ""
					c.properties  = {}
					c.insert()

