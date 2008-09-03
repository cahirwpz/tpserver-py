"""\
Player SQL Object
"""
# Module imports
from sqlalchemy import *

from tp.server.db import *

from tp.server.bases.SQL import SQLBase, SQLTypedBase, SQLTypedTable, quickimport
from tp.server.rules.dronesec.bases.Drone import Drone
from tp.server.rules.dronesec.bases.Research import Research

class Player(SQLBase):
	"""
	Player information needed to track available drones and researches
	"""
	table = Table('dronesec_player', metadata,
		Column('game', 	       Integer,     nullable=False, index=True, primary_key=True),
		Column('id',	       Integer,     nullable=False, index=True, primary_key=True),
		Column('type',	       Binary, nullable=False, index=True, default = 'Normal'),
		Column('drones',       PickleType,  nullable=False, default={}),
		Column('research',     PickleType,  nullable=False, default=[]),
		Column('researchLeft', PickleType,  nullable=False, default={}),
		Column('canResearch',  PickleType,  nullable=False, default = {}),
		Column('time',	       DateTime,    nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		ForeignKeyConstraint(['game'], ['game.id']),
	)

	def __str__(self):
		return "<Player id=%s>" % self.id


	def BuildList(self):
		"""
		BuildList()
		
		Builds the initial list of drones and researches without requirements for the player
		"""
		self.drones = {}
		self.research = set()
		self.canResearch = {}
		self.researchLeft = {}

		#Build Drones that can be built by this player
		for id, time in Drone.ids():
			if len(Drone(id).reqs) == 0:
				self.drones[id]= Drone(id).name

		#Build Researches that can be done by this player
		for id, time in Research.ids():
			if id not in self.research:
				if len(Research(id).reqs) == 0:
					self.canResearch[id] = Research(id).name


	def addDrone(self, drone):
		"""
		addDrone(drone)
		Adds a drone to the list of available drones
		
		drone - ID of the drone that is now available to the player.
		"""
		if not self.drones.has_key(drone):
			if Research.byname(Drone(drone).reqs) in self.research:
				self.drones[drone] =Drone(drone).name


	def addResearch(self, id):
		"""
		addResearch(id)
		
		Adds a research to a player and removes it from the lists
		Checks requirements and adds any research that is now available to the list
		"""
		if id not in self.research:
			self.research.add(id)
		if id in self.researchLeft.keys():
			del self.researchLeft[id]
		if id in self.canResearch.keys():
			del self.canResearch[id]

		posNew = Research.bylist(self.research)
		##FIXME: HACK!
		# By making the researches sets we can simplify things quickly to check subsets
		posNew = list(set(posNew) - set(self.canResearch.keys()))
		for x in posNew:
			reqList = set()
			for y in Research(x).reqs:
				reqList.add(Research.byname(y))
			if reqList:
				if reqList <= self.research:
					print "%s can now be researched" % Research(x).name

					self.canResearch[x] = Research(x).name


	def researchQuota(self, id, payed, ratio):
		"""
		researchQuota(id, payed, ratio)
		
		Adds the multiple of the amount payed and the ratio with the amount payed
		Checks if the research is finished
		
		id - The Research's ID
		payed - how many resources are being sent to pay for this Research
		ratio - The ratio bonus applied to the amount payed for this research
		"""
		if id not in self.researchLeft:
			self.researchLeft[id] = 0

		# Get the current difference between the cost and the amount payed so far
		check = Research(id).cost - self.researchLeft[id]
		# If the amount payed with the ration is more, then find the extra resources
		if check <= payed * ratio:
			extra = payed - (check / ratio)
		self.researchLeft[id] += payed * ratio


		# The function returns true so that the research order can know if it was finished
		if self.researchLeft[id] >= Research(id).cost:
			return True, extra
		else: return False, 0


	@classmethod
	def realid(cls, user, pid):
		"""
		realid(user, pid)
		
		Returns the real ID of the user
		"""
		if pid == 0:
			return user.id
		return pid
