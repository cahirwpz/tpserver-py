"""\
Calculates and resolves all combat conflicts
"""
import random
from tp.server.bases.Message import Message
from tp.server.utils import WalkUniverse
from tp.server.rules.dronesec.bases.Drone import Drone

from tp.server.rules.dronesec.research.ResearchCalculator import ResearchCalculator as RC

def do(top):
	"""
	Action method for FleetCombat
	
	All opposing Fleets at the same location engage in combat.
	Drones are destroyed as enough damage is dealt to surpass their health.
	"""
	#Get all Fleets
	def h(obj, d):
		# Check the object can go into combat (Drone Fleet)
		if not obj.type.endswith('objects.Fleet'):
			return

		# Check the object isn't owned by the universe
		if obj.owner == -1:
			return

		pos = obj.posx, obj.posy, obj.posz
		if not d.has_key(pos):
			d[pos] = []

		d[pos].append(obj)

	d = {}
	WalkUniverse(top, "before", h, d)

	for pos, fleets in d.items():
		if len(fleets) < 2:
			continue

		# Check that more than one player is around.
		if len(dict.fromkeys([fleet.owner for fleet in fleets])) <= 1:
			continue

		# create sides
		# Assumption: Technically each fleet consists of a single ship type.
		sides = dict()
		sideTypes = dict()
		for fleet in fleets:
			if not sides.has_key(fleet.owner):
				sides[fleet.owner] = []
			if not sideTypes.has_key(fleet.owner):
				sideTypes[fleet.owner] = dict()

			sides[fleet.owner].append(fleet)
			t = Drone(fleet.ships.keys()[0]).type
			if not sideTypes[fleet.owner].has_key(t):
				sideTypes[fleet.owner][t] = []

			#Append the fleet and their current damage taken
			sideTypes[fleet.owner][t].append([fleet, fleet.damage])

		#### This is very a simple combat implementation
		#### This is a quick hack to get it going

		rand = random.Random()
		for side, fleets in sides.items():
			for fleet in fleets:
				fleetAttack, fleetNumAttacks, fleetHealth = RC.Combat(fleet.owner, fleet.ships.keys()[0])
				for times in range(fleetNumAttacks):
					# HACK: Since fleets should have only 1 ship type this should work
					attackedSide = side
					while attackedSide == side:
						attackedSide = rand.randint(1, len(sides.keys()))
					findType = Drone(fleet.ships.keys()[0]).strength
					if not (findType == 'All' or findType == 'None') \
						and sideTypes[attackedSide].has_key(findType):

						t = findType
					else: 
						#If you don't have a bonus then pick a type randomly
						typeList = sideTypes[attackedSide].keys()
						t =typeList[rand.randint(0, len(typeList) -1)]
					rInt = rand.randint(0,len(sideTypes[attackedSide][t]) -1)
					# Fleet deals all of its damage to that fleetl
					defender = sideTypes[attackedSide][t][rInt]

					# Bonus Damage checks
					damageDone = fleet.damage_get()
					bonusRatio = 1
					fleetType = Drone(fleet.ships.keys()[0]).type
					# Attacker Modifiers
					if Drone(fleet.ships.keys()[0]).strength == 'All':
						bonusRatio += .25
					elif t == Drone(fleet.ships.keys()[0]).strength:
						bonusRatio += .25
					elif t == Drone(fleet.ships.keys()[0]).weakness:
						bonusRatio -= .25
					# Defender moodifiers
					if Drone(defender[0].ships.keys()[0]).weakness == 'All':
						bonusRatio += .25
					elif Drone(defender[0].ships.keys()[0]).weakness == fleetType:
						bonusRatio += .25
					elif Drone(defender[0].ships.keys()[0]).strength == fleetType:
						bonusRatio -= .25
					defender[1] += damageDone * bonusRatio
					diff = damageDone - (defender[0].total_health() - defender[1])
					defender[0].damage = defender[1]
					defender[0].save()
					while diff > 0:
						rInt = rand.randint(0,len(sideTypes[attackedSide][t]) -1)
						# Fleet deals all of its damage to that fleet
						defender = sideTypes[attackedSide][t][rInt]
						defender[1] += diff
						diff = diff - (defender[0].total_health() - defender[1])
						defender[0].damage = defender[1]
						defender[0].save()

						# Check to see if the extra damage has been transferred
						if diff < fleetAttack:
							diff =0
							continue

						# Check to end combat if all units of this type have been destroyed
						totalh = 0
						totald = 0
						for fleet, damage in sideTypes[attackedSide][t]:
							totalh += fleet.total_health()
							totald += damage
						if totald > totalh:
							diff = 0

		 #Resolve combat by having units take the damage so they can be killed/ghoster
		for side, fleets in sides.items():
			for fleet in fleets:
				fleet.damage_do()
				fleet.save()
