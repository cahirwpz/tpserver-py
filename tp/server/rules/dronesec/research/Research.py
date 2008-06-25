#Research class. holds all relevant information on them.

class Research:
	def __init__(self, id, name, abbrev, cost, *args):
		self.id = id
		self.name = name
		self.abbrev = abbrev
		self.cost = cost
		self.requirements = args

