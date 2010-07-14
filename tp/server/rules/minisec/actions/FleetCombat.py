"""\
This module impliments combat as found in the MiniSec document.
"""

from copy import copy
import random
import pprint
import math

class Choice(object):
	choices = ('Rock', 'Paper', 'Scissors')
	
	def __init__(self, choice=None, rand=None):
		if rand != None:
			choice = rand.choice(self.choices)
			
		if not choice in self.choices:
			raise ValueError("Not a valid choice.")
		
		self.choice = choice

	def __eq__(self, other):
		if self.choice == other.choice:
			return True
		else:
			return False
			
	def __gt__(self, other):
		winnings = (('Paper', 'Rock'), ('Scissors', 'Paper'), ('Rock', 'Scissors'))
		return (self.choice, other.choice) in winnings

	def __lt__(self, other):
		return not (self.__gt__(other) or self.__eq__(other))

	def __str__(self):
		return "<Choice %s>" % self.choice
	__repr__ = __str__

class Damage(int):
	"""\
	An integer which tracks where it came from.
	"""
	def __new__(cls, source, amount):
		return int.__new__(cls, amount)

	def __init__(self, source, amount):
		self.source = source

class Ships(list):
	"""
	Class which defines the number of ships at this location

	If split is given true, planets and homeworlds are considered in their
	"battery" components.
	"""

	BATTLESHIP = 0
	FRIGATE    = 1
	SCOUT      = 2
	PLANET     = 3
	HOMEWORLD  = 4
	PLANET_EQV = 2
	HOME_EQV   = 5

	names    = ['battleship', 'frigate', 'scout', 'planet', 'homeworld'] 	# Names of the ships
	strength = [6, 6, 6, 4, 2] 												# How many HP each ship has
	damage   = [(3, 1), (2, 0), (0, 0), (3, 1), (3, 1)] 					# How much damage the ship does (win, draw)

	def __init__(self, l=[], split=False):
		list.__init__(self, l)
		self.split = split

	def __str__(self):
		s = "[Ships "

		if self.split:
			things = ['battleships', 'frigates', 'scouts', 'planet-batteries', 'homeworld-batteries']
		else:
			things = ['battleships', 'frigates', 'scouts', 'planets', 'homeworld']
		for i, name in enumerate(things):
			if self[i] > 0:
				s += " %s:%s" % (name, self[i])
		return s + ']'
	__repr__ = __str__

	def combine(self):
		if self.split:
			return [self[Ships.BATTLESHIP], self[Ships.FRIGATE], self[Ships.SCOUT], 
				int(math.ceil(1.0*self[Ships.PLANET]/Ships.PLANET_EQV)), 
				int(math.ceil(1.0*self[Ships.HOMEWORLD]/Ships.HOME_EQV))]
		else:
			return self

	def addships(self, Battleship=0, Frigate=0, Scout=0, Planet=0, Homeworld=0):
		self[0] += Battleship
		self[1] += Frigate
		self[2] += Scout
		self[3] += Planet
		self[4] += Homeworld

class Side(object):
	"""\
	A class which keeps track of how many ships a side has.
	"""

	dead = [] # Marker which means a ship is dead

	def __init__(self, owner, battleships, frigates, scouts, planets, homeworld):
		self.owner  = owner
		self.ships  = Ships([battleships, frigates, scouts, planets*Ships.PLANET_EQV, homeworld*Ships.HOME_EQV], split=True)
		self.initdamage()

	def initdamage(self):
		self.damages = []
		for amount in self.ships:
			self.damages.append([])
			for j in range(0, int(amount)):
				self.damages[-1].append(0)

	def addships(self, **kw):
		self.ships.addships(**kw)
		self.initdamage()

	def __str__(self):
		return "<Side %s>" % self.owner
	__repr__ = __str__	
	
	def escape(self):
		"""\
		Returns the chance of escape.
		"""
		# Can't escape if we are defending our planets.
		if (self.ships[Ships.PLANET]+self.ships[Ships.HOMEWORLD]) > 0:
			return 0 
		return self.ships[Ships.SCOUT] * 100.0/(self.ships[Ships.SCOUT] + self.ships[Ships.FRIGATE] + self.ships[Ships.BATTLESHIP])

	def fire(self, win=True):
		"""\
		Returns the damage this fleet will do.
		"""
		damages = []
		for type, amount in enumerate(self.ships):
			damage = Ships.damage[type][not win]

			if damage > 0:
				for index in range(0, amount):
					damages.append(Damage(self.name(type, index), damage))
		return damages

	def damage(self, points, bxml=None):
		"""\
		Applies damage to this fleet.
		"""
		points = copy(points)

		death = Ships([0, 0, 0, 0, 0])
		while len(points) > 0:
			damage = points.pop(0)

			# Find the least damaged most powerful ship
			index = -1
			type  = 0
			for type, damages in enumerate(self.damages):
				try:
					smallest = min(damages)
					if smallest is self.dead:
						continue
					index = damages.index(smallest)
					break
				except ValueError, e:
					pass

			if index == -1:
				break
	
			self.damages[type][index] += damage

			if bxml:
				bxml.fire(damage.source, self.name(type, index))
				bxml.damage(self.name(type, index), damage)

			if self.damages[type][index] >= Ships.strength[type]:
				type = self.remove(type, index)

				if type > -1:
					if bxml:
						bxml.death(self.name(type, index))
					death[type] += 1

		return death

	def name(self, type, index):
		"""\
		Returns a unquie "name" for a ship in this side (from type and index).
		"""
		if type == Ships.PLANET:
			index = index / Ships.PLANET_EQV
		if type == Ships.HOMEWORLD:
			index = index / Ships.HOME_EQV
		return "%s-%s-%i" % (self.owner, Ships.names[type], index)

	def remove(self, type, index):
		"""\
		Removes a ship from the side, returns if this meant there was a death
		in that type. (For example you need to remove all batteries from a 
		planet before it died.)
		"""

		# Remove the ship
		self.damages[type][index] = self.dead
		self.ships[type] -= 1

		if type == Ships.PLANET:
			if self.ships[Ships.PLANET] % Ships.PLANET_EQV != 0:
				return -1
		if type == Ships.HOMEWORLD:
			if self.ships[Ships.HOMEWORLD] % Ships.HOME_EQV != 0:
				return -1
		return type

	def empty(self):
		"""\
		Returns if the number of ships is == 0
		"""
		return reduce(int.__add__, self.ships, 0) == 0
	empty = property(empty)

class Stats(dict):
	"""
	Records various stats about the Battle.
	"""

	def __init__(self):
		self.rounds = 0

	def init(self, id):
		"""\
		Initialises the stats information for a side.
		"""
		if self.has_key(id):
			return
		self[id] = {
			'wins':   0, 'loses': 0, 'draws': 0,
			'damage': {'taken': 0, 'delt': 0},
			'choices': {'rock':0, 'paper':0, 'scissors':0},
			'lost':   Ships([0, 0, 0, 0, 0]),
			'killed': Ships([0, 0, 0, 0, 0])}

	def winner(self, id):
		self[id]['wins']  += 1
	def loser(self, id):
		self[id]['loses'] += 1
	def draw(self, id):
		self[id]['draws'] += 1

	def choice(self, id, value):
		self[id]['choices'][value.choice.lower()] += 1

	def damage(self, src, dst, points):
		total = reduce(int.__add__, points)
		self[src]['damage']['delt'] += total
		self[dst]['damage']['taken'] += total

	def round(self):
		self.rounds += 1
		print "Round ", self.rounds

	def killed(self, src, dst, battleships=0, frigates=0, scouts=0, planets=0, homeworld=0):
		ships = [battleships, frigates, scouts, planets, homeworld]
		for i,v in enumerate(ships):
			self[src]['killed'][i] += v
			self[dst]['lost'][i]   += v

# Need to find an ElementTree implimentation!
ET = None
errors = []
try:
	import elementtree.ElementTree as ET
except ImportError, e:
	errors.append(e)
try:
	import cElementTree as ET
except ImportError:
	errors.append(e)
try:
	import lxml.etree as ET
except ImportError:
	errors.append(e)
try:
	import xml.etree.ElementTree as ET
except ImportError:
	errors.append(e)
if ET is None:
	raise ImportError(str(errors))

def indent(elem, level=0):
	"""
	Simple helper function to indent an ElementTree before outputing it.
	"""
	i = "\n" + level*"  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		for elem in elem:
			indent(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

class BattleXML(object):
	"""
	A class to output BattleXML data.
	"""
	def __init__(self):
		self.root = ET.Element('battle', version='0.0.1', media='minisec')
		self.sides  = ET.SubElement(self.root, "sides")
		self.rounds = ET.SubElement(self.root, "rounds")

	def init(self, side):
		self.sides.append(ET.Element("side", id=side.owner))
		sidexml = self.sides[-1]

		for type, amount in enumerate(side.ships.combine()):
			for index in range(0, amount):
				entityid = side.name(type, index)

				sidexml.append(ET.Element("entity", id=entityid))
				entityxml = sidexml[-1]
				
				namexml = ET.SubElement(entityxml, "name")
				namexml.text = entityid

				typexml = ET.SubElement(entityxml, "type")
				typexml.text = side.ships.names[type]

	def round(self):
		self.rounds.append(ET.Element('round', number=str(len(self.rounds))))

	def log(self, s):
		logxml = ET.Element('log')
		logxml.text = s
		self.rounds[-1].append(logxml)

	def fire(self, src, dst):
		self.rounds[-1].append(ET.Element("fire"))
		firexml = self.rounds[-1][-1]

		firexml.append(ET.Element("source", ref=src))
		firexml.append(ET.Element("destination", ref=dst))

	def damage(self, ref, amount):
		self.rounds[-1].append(ET.Element("damage"))
		damagexml = self.rounds[-1][-1]
		
		damagexml.append(ET.Element("reference", ref=ref))
		damagexml.append(ET.Element("amount"))
		amountxml = damagexml[-1]
		amountxml.text = str(amount)

	def death(self, ref):
		self.rounds[-1].append(ET.Element("death"))
		self.rounds[-1][-1].append(ET.Element("reference", ref=ref))

	def output(self):
		indent(self.root)
		return ET.tostring(self.root)

def combat(working, bxmloutput=None):
	working = list(working)
	print "Starting combat with", working
	rand = random.Random()
 
	messages = {}
	stats = Stats()
	bxml  = BattleXML()
	
	# Setup the sides
	for side in working:
		s = ""
		others = [other for other in working if other != side]
		while len(others) > 0:
			other = others.pop(0)
			if other == side:
				continue
			if len(others) >= 2:
				s+= "%s, " % other.owner
			elif len(others) >= 1:
				s+= "%s and " % other.owner
			else:
				s+= "%s" % other.owner

		messages[side.owner] = ['A battle was started against %s' % s]

		bxml.init(side)
		stats.init(side.owner)

	while len(working) >= 2:
		bxml.round()
		stats.round()

		while True:
			red, blue = (rand.choice(working), rand.choice(working))
			if red != blue:
				break

		print "The following sides will participate in this round:", red, blue
		print red, red.ships
		print blue, blue.ships

		# Figure out who chooses what
		choices = (Choice(rand=rand), Choice(rand=rand))
		stats.choice(red.owner, choices[0]), stats.choice(blue.owner, choices[1])
		bxml.log("%s choose %s." % (red.owner,  choices[0].choice) )
		bxml.log("%s choose %s." % (blue.owner, choices[1].choice) )
		if choices[0] == choices[1]:
			print "Round was a draw!"
			bxml.log("Round was a draw!")

			# Draw
			stats.draw(red.owner)
			stats.draw(blue.owner)

			brd = blue.fire(False)
			rbd = red.fire(False)

			if len(brd) > 0:
				stats.damage(blue.owner, red.owner, brd)
				death = blue.damage(rbd, bxml)
				stats.killed(red.owner, blue.owner, *death)

			if len(rbd) > 0:
				stats.damage(red.owner, blue.owner, rbd)
				death = red.damage(brd, bxml)
				stats.killed(blue.owner, red.owner, *death)

		else:
			# One side won
			if choices[0] >= choices[1]:
				print red, "won the round!"
				bxml.log("%s won the round!" % red.owner)
				winner, loser = red, blue
			if choices[0] <= choices[1]:
				print blue, "won the round!"
				bxml.log("%s won the round!" % blue.owner)
				winner, loser = blue, red

			# See if the winning fleet has escaped?
			a, b =  winner.escape(), (1-rand.random())*100
			if a > b:
				bxml.log("%s has escaped. (%s got %s)" % (winner.owner, a, b))
				print "%s has escaped. (%s got %s)" % (winner, a, b)
				messages[winner.owner].append("Your fleet escaped from battle.")

				for side in working:
					if side == winner:
						continue
					messages[side.owner].append("%s's fleet cowardly ran away." % winner.owner)
				working.remove(winner)
				continue

			stats.winner(winner.owner)
			stats.loser(loser.owner)

			damage = winner.fire(True)
			if len(damage) > 0:
				stats.damage(winner.owner, loser.owner, damage)
				death = loser.damage(damage, bxml)
				stats.killed(winner.owner, loser.owner, *death)

		# See is anything has died
		for side in [blue, red]:
			if side.empty:
				bxml.log("%s was knocked out of the battle." % side.owner)
				print side, "was knocked out of the battle."
				working.remove(side)
				messages[side.owner].append("Your fleet was totally destoryed.")

				for other in working:
					messages[other.owner].append("%s's fleet was totally destoryed." % side.owner)

	if not bxmloutput is None:
		print >> bxmloutput, bxml.output()
	pprint.pprint(messages)

	print "--Stats--"
	for side in stats.keys():
		pprint.pprint(stats[side])
	return

##	# Build messages for all the participants
##	try:
##		winner = (class1+class2)[0].owner
##	except IndexError:
##		winner = 0
##		
##	for owner in participants:
##		m = Message()
##		m.bid = owner
##		m.slot = -1
##		
##		m.body = ""
##		if owner == winner:
##			m.subject = "Battle won!"
##			m.body += "You have been <b>victorious</b> in a battle at %s, %s, %s.<br>" % pos
##		else:
##			m.subject = "Battle lost!"
##			m.body += "You have been <b>defeated</b> in a battle at %s, %s, %s.<br>" % pos
##			
##		m.body += "<br>Summary as follows:<br>"
##
##		you = ""
##		other = ""
##		for downer, message in messages:
##			if downer != owner:
##				other += "\t<li>%s's %s</li>\n" % (downer, message)
##			else:
##				you += "\t<li>Your %s</li>\n" % message
##				
##		m.body += "<ul>%s</ul><ul>%s</ul>" % (you, other)
##		m.insert()

from tp.server.rules.base import Action, Combatant
from tp.server.utils import WalkUniverse

class FleetCombatAction( Action ):
	def __call__( self, top ):
		def h(obj, d):
			# Check the object can go into combat
			if not isinstance(obj, Combatant):
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
				
			if len(dict.fromkeys([fleet.owner for fleet in fleets])) <= 1:
				continue
		
			# Build the sides
			sides = {}
			for fleet in fleets:
				if not sides.has_key(fleet.owner):
					sides[fleet.owner] = Side(fleet.owner, 0, 0, 0, 0, 0)

				if fleet.type.endswith("Planet"):
					sides[fleet.owner].addships(Planet=1)
				else:
					for type, amount in fleet.ships.items():
						sides[fleet.owner].addships(**{['Scout', 'Frigate', 'Battleship'][type]: amount})

			r = combat(sides.values())

def main():
	"""\
FleetCombat.py <file name>

Input file format,
<side name> <number of battleships> <number of frigates> <number of scouts> <number of planets> <number of homeworlds>
	"""
	import sys
	if len(sys.argv) == 1:
		print main.__doc__
		return

	import os
	if not os.path.exists(sys.argv[1]):
		print main.__doc__
		return	

	if len(sys.argv) == 3:
		bxmloutput = file(sys.argv[2], 'w')
	else:
		bxmloutput = None

	sides = []

	f = file(sys.argv[1], 'r')
	for line in f.readlines():
		data = line.split(' ')
		sides.append(Side(data[0], *[int(x) for x in data[1:]]))

	print sides

	combat(sides, bxmloutput)

	print "Ships remaining:"
	for side in sides:
		print side, side.ships


if __name__ == "__main__":
	main()

__all__ = [ 'FleetCombatAction' ]
