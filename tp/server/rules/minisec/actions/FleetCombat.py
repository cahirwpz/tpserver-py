

import random

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



if __name__ == "__main__":
	pass

# Figure out which people are in combat
	# Planets? Multiple Fleets of same owner?
