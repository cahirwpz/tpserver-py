"""\
This module impliments combat as found in the MiniSec document.
"""

from copy import copy
import random
import pprint

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


BATTLESHIP = 0
FRIGATE    = 1
SCOUT      = 2
PLANET     = 3
HOMEWORLD  = 4
PLANET_EQV = 2
HOME_EQV   = 5
class Ships(list):
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

class Side(object):
	def __init__(self, owner, battleships, frigates, scouts, planets, homeworld):
		self.owner  = owner
		self.ships  = Ships([battleships, frigates, scouts, planets*PLANET_EQV, homeworld*HOME_EQV], split=True)
		self.damages = []
		for amount in [self.battleship_equiv(), self.ships[FRIGATE], self.ships[SCOUT]]:
			self.damages.append([])
			for j in range(0, int(amount)):
				self.damages[-1].append(0)

	def __str__(self):
		return "<Side %s>" % self.owner
	__repr__ = __str__	

	def escape(self):
		"""\
		Returns the chance of escape.
		"""
		# Can't escape if we are defending our planets.
		if (self.ships[PLANET]+self.ships[HOMEWORLD]) > 0:
			return 0 
		return self.ships[SCOUT] * 100.0/(self.ships[SCOUT] + self.ships[FRIGATE] + self.ships[BATTLESHIP])

	def fire(self, win):
		"""\
		Returns the damage this fleet will do.
		"""
		if win:
			return [3]*self.battleship_equiv() + [2]*int(self.ships[FRIGATE])
		else:
			return [1]*self.battleship_equiv()

	def battleship_equiv(self):
		return int(self.ships[BATTLESHIP]+self.ships[PLANET]+self.ships[HOMEWORLD])

	def damage(self, points):
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
					index = damages.index(smallest)
					break
				except ValueError:
					pass

			if index == -1:
				break
	
			self.damages[type][index] += damage

			# Now is this over?
			if self.damages[type][index] >= {BATTLESHIP:6, FRIGATE:4, SCOUT:2}[type]:
				type = self.remove(type, index)
				if type > -1:
					death[type] += 1
		return death

	def remove(self, type, index):
		del self.damages[type][index]
		if type == BATTLESHIP:
			if self.ships[BATTLESHIP] > 0:
				self.ships[BATTLESHIP] -= 1
				return BATTLESHIP
			elif self.ships[PLANET] > 0:
				self.ships[PLANET] -= 1
				if self.ships[PLANET] % PLANET_EQV == 0:
					return PLANET
			elif self.ships[HOMEWORLD] > 0:
				self.ships[HOMEWORLD] -= 1
				if self.ships[HOMEWORLD] % HOME_EQV == 0:
					return HOMEWORLD
			else:
				raise RuntimeError("Somehow we did damage to a battleship like object which didn't exist.")
			return -1
		self.ships[type] -= 1
		return type

	def size(self):
		return reduce(int.__add__, self.ships, 0)
	size = property(size)

class Stats(dict):
	def __init__(self):
		self.rounds = 0

	def init(self, id):
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

def combat(*working):
	working = list(working)
	print "Starting combat with", working
	rand = random.Random()
 
	messages = {}
	stats = Stats()
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
		stats.init(side.owner)

	while len(working) >= 2:
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
		if choices[0] == choices[1]:
			print "Round was a draw!"

			# Draw
			stats.draw(red.owner)
			stats.draw(blue.owner)

			brd = blue.fire(False)
			rbd = red.fire(False)

			if len(brd) > 0:
				stats.damage(blue.owner, red.owner, brd)
				death = blue.damage(brd)
				stats.killed(red.owner, blue.owner, *death)

			if len(rbd) > 0:
				stats.damage(red.owner, blue.owner, rbd)
				death = red.damage(rbd)
				stats.killed(blue.owner, red.owner, *death)

		else:
			# One side won
			if choices[0] >= choices[1]:
				print red, "won the round!"
				winner, loser = red, blue
			if choices[0] <= choices[1]:
				print blue, "won the round!"
				winner, loser = blue, red

			# See if the winning fleet has escaped?
			a, b =  winner.escape(), (1-rand.random())*100
			if a > b:
				print winner, "has escaped. (%s got %s)" % (a, b)
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
				death = loser.damage(damage)
				stats.killed(winner.owner, loser.owner, *death)

		# See is anything has died
		for side in [blue, red]:
			if side.size == 0:
				print side, "was knocked out of the battle."
				working.remove(side)
				messages[side.owner].append("Your fleet was totally destoryed.")

				for other in working:
					messages[other.owner].append("%s's fleet was totally destoryed." % side.owner)

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

def do(top):
	from tp.server.bases.Combattant import Combattant

	from tp.server.bases.Message import Message
	from tp.server.utils import WalkUniverse

	def h(obj, d):
		# Check the object can go into combat
		if not isinstance(obj, Combattant):
			return

		# Check the object isn't owned by the universe
		if obj.owner == -1:
			return

		pos = obj.posx, obj.posy, obj.posz
		if not d.has_key(pos):
			d[pos] = [[], []]

		d[pos][obj.type == "sobjects.Planet"].append(obj)

	d = {}
	WalkUniverse(top, "before", h, d)

	for pos, fleets in d.items():
		if len(fleets[0]+fleets[1]) < 2:
			continue
			
		if len(dict.fromkeys([fleet.owner for fleet in fleets[0]+fleets[1]])) <= 1:
			continue
			
		r = combat(*fleets)


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

	sides = []

	f = file(sys.argv[1], 'r')
	for line in f.readlines():
		data = line.split(' ')
		sides.append(Side(data[0], *[int(x) for x in data[1:]]))

	print sides

	combat(*sides)

	print "Ships remaining:"
	for side in sides:
		print side, side.ships


if __name__ == "__main__":
	main()
