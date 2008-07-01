"""\
Resources require to build stuff.
"""
# Module imports
from sqlalchemy import *

from tp.server.db import *

from tp.server.bases.SQL import SQLBase
from tp.server.rules.dronesec.bases.Drone import Drone
from tp.server.rules.dronesec.bases.Research import Research

class Player(SQLBase):
	table = Table('player', metadata,
		Column('game', 	       Integer,     nullable=False, index=True, primary_key=True),
		Column('id',	       Integer,     nullable=False, index=True, primary_key=True),
		Column('drones',       Binary,      nullable=False, default={}),
		Column('research',     Binary,      nullable=False, default=[]),
		Column('researchLeft', Binary,      nullable=False, default={}),
		Column('canResearch',  Binary,      nullable=False, default = {}),
		Column('time',	       DateTime,    nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		ForeignKeyConstraint(['game'], ['game.id']),
	)


	def __str__(self):
		return "<User id=%s username=%s>" % (self.id, self.username)


	def __init__(self):
		self.drones = {}
		self.research = []
		self.canResearch = {}
		self.researchLeft = {}

		#Build Drones that can be built by this player
		for id, time in Drone.ids():
			if len(Drone(id).reqs[id]) == 0:
				self.drones[id]= Drone(id).name

		#Build Researches that can be done by this player
		for id, time in Research.ids():
			if id not in self.research:
				if len(Research(id).reqs) == 0:
					self.canResearch[id] = Research(id).name

				SQL.__init__(self, id)

	def addDrone(self, drone):
		if not self.drones.has_key(drone):
			if Drone(id).reqs in self.research:
				self.drones[drone] =Drone(drone).name


	def addResearch(self, id):
		if id not in self.research:
			self.research.append(research)
		if id in self.researchLeft.keys():
			del self.researchLeft[id]
		if id in self.canResearch.keys():
			del self.canResearch[id]


	def researchQuota(self, id, payed):
		if id not in self.researchLeft:
			self.researchLeft[id] = 0
		self.researchLeft[id] += payed

		if self.researchLeft[id] >= Research(id).cost:
			return True, self.researchLeft[id] - Research(id).cost
		else: return False, 0


	@classmethod
	def realid(cls, user, pid):
		if pid == 0:
			return user.id
		return pid

