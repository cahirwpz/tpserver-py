"""\
Resources require to build stuff.
"""
# Module imports
from sqlalchemy import *

from tp.server.db import *

from tp.server.bases.SQL import SQLBase, SQLTypedBase, SQLTypedTable, quickimport
from tp.server.rules.dronesec.bases.Drone import Drone
from tp.server.rules.dronesec.bases.Research import Research

class Player(SQLBase):
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
		return "<Player id=%s>" % (self.id, self.username)


	def BuildList(self):
		self.drones = {}
		self.research = []
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

		if not self.drones.has_key(drone):
			if Research.byname(Drone(drone).reqs) in self.research:
				self.drones[drone] =Drone(drone).name


	def addResearch(self, id):
		if id not in self.research:
			self.research.append(id)
		if id in self.researchLeft.keys():
			del self.researchLeft[id]
		if id in self.canResearch.keys():
			del self.canResearch[id]

		posNew = Research.byreq(Research(id).abbrev)
		for x in posNew:
			reqList = []
			for y in Research(x).reqs:
				reqList.append(Research.byname(y))
				if reqList in self.research:
					self.canResearch[x] = Research(x).name


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
