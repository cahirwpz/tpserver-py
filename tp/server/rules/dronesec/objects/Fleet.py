
from sqlalchemy import *

from types import TupleType, ListType

from tp.server.bases.Object import Object
from tp.server.bases.Design import Design
from tp.server.bases.Combattant import Combattant
from tp.server.rules.dronesec.bases.Player import Player
from tp.server.rules.dronesec.bases.Drone import Drone
from tp.server.rules.dronesec.bases.Research import Research

class Fleet(Object, Combattant):
	attributes = { \
		'owner': Object.Attribute('owner', -1, 'public'),
		'ships': Object.Attribute('ships', {}, 'protected'),
		'damage': Object.Attribute('damage', 0, 'protected'),
		'target': Object.Attribute('target', (0, 0, 0), 'private'),
		'ordered': Object.Attribute('ordered', 0, 'private'),
	}
	orderclasses = (
		)

	def calcPower(self):
		power = 0
		for type, no in self.ships.items():
			power += Drone(type).power * no
			researches = Research.bytype('tp.server.rules.dronesec.research.WorldType')
			res = []
			for x in Player(self.owner).research:
				if x in researches:
					res.append(x)
			researches = res
			if researches:
				for id in researches:
					if Drone(type).type in Research(id).types or Drone(type).name in Research(id).units  or 'All' in Research(id).types:
						power += Research(id).power * no

		return power

	def fn_damage(self, value = None):
		return int(self.damage)

	def fn_ships(self, value=None):
		if value == None:
			return self.ships.items()

	def fn_name(self, value=None):
		if value == None:
			return (255, self.name)
		else:
			self.name = value[1]

	def tidy(self):
		"""\
		Fix up the ships and damage stuff.
		"""
		# Run a consistancy check
		# Check the ships actually exist
		for t, number in self.ships.items():
			if number < 1:
				del self.ships[t]

	def ghost(self):
		"""\
		Returns if the fleet has no ships.
		"""
		self.tidy()
		return len(self.ships.keys()) < 1

	#############################################
	# Movement functions
	#############################################
	def speed(self):
		"""\
		Returns the maximum speed of the fleet.
		"""
		types = dict()
		for ship in self.ships.keys():
			types[ship] = Drone(ship).speed
		slowDrone = min(types,key = lambda a: types.get(a))
		speed = Drone(slowDrone).speed
		print "Normal speed was %i" % speed
		researches = Research.bytype('tp.server.rules.dronesec.research.WorldType')
		speedRatio = 1
		res = []
		for x in Player(self.owner).research:
			if x in researches:
				res.append(x)
		researches = res
		if researches:
			for id in researches:
				if Drone(slowDrone).type in Research(id).types or Drone(slowDrone).name in Research(id).units or 'All' in Research(id).types:
					speedRatio += Research(id).speedRatio
					speed += Research(id).speed
		print "Speed with researches is %i" % (speed * speedRatio)
		return int(speed * speedRatio)

	#############################################
	# Combat functions
	#############################################

	def dead(self):
		"""\
		Checks if this object is a can still participate in combat.
		"""
		return self.ghost() or self.ships.keys() == [0,]

	def damage_do(self):
		"""\
		Damages a fleet.
		"""

		for type, no in self.ships.items():
			
			health = Drone(type).health
			
			researches = Research.bytype('tp.server.rules.dronesec.research.CombatType')
			res = []
			for x in Player(self.owner).research:
				if x in researches:
					res.append(x)
			researches = res
			if researches:
				for id in researches:
					if Drone(type).type in Research(id).types or Drone(type).name in Research(id).ships or 'All' in Research(id).types:
						health += Research(id).health

			while self.damage > health and self.ships[type] > 0:
				self.damage -= health
				self.ships[type] -= 1

	def damage_get(self, fail=False):
		"""\
		Returns the amount of damage this fleet can do.
		"""
		r = 0
		for type, no in self.ships.items():
			researches = Research.bytype('tp.server.rules.dronesec.research.CombatType')
			res = []
			for x in Player(self.owner).research:
				if x in researches:
					res.append(x)
			researches = res
			if researches:
				for id in researches:
					if Drone(type).type in Research(id).types or Drone(type).name in Research(id).ships or 'All' in Research(id).types:
						r += Research(id).damage * no
			r += Drone(type).attack * no
		return r

	def total_health(self):
		health = 0

		for type, num in self.ships.items():
			researches = Research.bytype('tp.server.rules.dronesec.research.CombatType')
			res = []
			for x in Player(self.owner).research:
				if x in researches:
					res.append(x)
			researches = res
			if researches:
				for id in researches:
					if Drone(type).type in Research(id).types or Drone(type).name in Research(id).ships or 'All' in Research(id).types:
						health += Research(id).health * num



			health += Drone(type).health * num
		return health

Fleet.typeno = 4
Object.types[Fleet.typeno] = Fleet
