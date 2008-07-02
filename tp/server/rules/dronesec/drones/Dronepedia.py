#Dronepedia loads the Drones to the database for a game.

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
		for name, typ, cost, power, attack, numAttacks, health, speed, strength, weakness, requirements in reader:
			if name != 'Name':
				from tp.server.rules.dronesec.bases.Drone import Drone
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

