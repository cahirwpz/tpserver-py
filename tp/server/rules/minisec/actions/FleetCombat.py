"""\
This module impliments combat as found in the MiniSec document.
"""

import random

from turn import WalkUniverse
from sbases.Combattant import Combattant
from sbases.Message import Message

class Choice:
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

def combat(pos, class1, class2):
	participants = dict.fromkeys([fleet.owner for fleet in class1+class2]).keys()

	print "Starting combat with", class1, "and", class2
	rand = random.Random()
 
	messages = []
	while True:
		owners = dict.fromkeys([fleet.owner for fleet in class1+class2])
		if len(owners) <= 1:
			break

		working = list(class1)
		if len(working) <= 1:
			working += class2

		#
		# Pick two from the fleets
		#
		while True:
			red, blue = (rand.choice(working), rand.choice(working))

			if red.owner != blue.owner:
				break
		
		#
		# Do the combat
		#
		choices = (Choice(rand=rand), Choice(rand=rand))
		if choices[0] >= choices[1]:
			blue.damage_do(red.damage_get(choices[0] == choices[1]))
		if choices[0] <= choices[1]:
			red.damage_do(blue.damage_get(choices[0] == choices[1]))

		#
		# See is anything has died
		#
		for fleet in blue, red:
			if fleet.dead():
				print "Dead", fleet
				if fleet in class1:
					if not fleet.ghost():
						messages.append((fleet.owner, "fleet %s was reduced to non-combat ships." % fleet.name))
					else:
						messages.append((fleet.owner, "fleet %s was destroyed in the battle." % fleet.name))
					class1.remove(fleet)
				elif red in class2:
					messages.append((fleet.owner, "planet %s was depopulated in the battle." % fleet.name))
					class1.remove(fleet)
					fleet.owner = 0

	messages.sort()
	# Build messages for all the participants
	try:
		winner = (class1+class2)[0].owner
	except IndexError:
		winner = 0
		
	for owner in participants:
		m = Message()
		m.bid = owner
		m.slot = Message.number(m.bid)
		
		m.body = ""
		if owner == winner:
			m.subject = "Battle won!"
			m.body += "You have been victorious in a battle at %s, %s, %s.\n" % pos
		else:
			m.subject = "Battle lost!"
			m.body += "You have been defeated in a battle at %s, %s, %s.\n" % pos
			
		m.body += "\nSummary as follows:\n"

		you = ""
		other = ""
		for downer, message in messages:
			if downer != owner:
				other += "\t%s's %s\n" % (downer, message)
			else:
				you += "\tYour %s\n" % message
				
		m.body += you
		m.body += other
		m.insert()

def do(top):
	def h(obj, d):
		if not isinstance(obj, Combattant):
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
			
		r = combat(pos, *fleets)
