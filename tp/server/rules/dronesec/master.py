#Holds each game's relevant information

from tp.server.rules.dronesec.drones.Dronepedia import Dronepedia
from tp.server.rules.dronesec.research.MasterList import MasterList
from tp.server.rules.dronesec.research.PlayerList import PlayerList
from tp.server.rules.dronesec.drones.DroneAvailability import DroneAvailability
from tp.server.bases.Game import Game

import shelve
import os

class Controller:
	def __init__(self):
		self.DP = {}
		self.ML = {}
		self.PL = {}
		self.DA = {}
		try:
			self.load()
		except IOError:
			print "oops"
		self.save()

	def load(self):
		try:
			f = 'master.dbm'
			try:
				filehandler = shelve.open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/"),f), 'r')
			except:
				filehandler = shelve.open(f, 'r')
			self.DA = filehandler['DA']
			self.DP = filehandler['DP']
			self.ML = filehandler['ML']
			self.PL = filehandler['PL']
			filehandler.close()
		except:
			print "No file exists to be loaded. Creating new type"


	def save(self):
		f = 'master.dbm'
		try:
			filehandler = shelve.open(os.path.join(os.path.abspath("./tp/server/rules/dronesec/"),f), 'n')
		except:
			filehandler = shelve.open(f, 'n')

		filehandler['DA'] = self.DA
		filehandler['DP'] = self.DP
		filehandler['ML'] = self.ML
		filehandler['PL'] = self.PL

		filehandler.close()

	def addGame(self, game):
		self.DP[game] = Dronepedia()
		self.ML[game] = MasterList()
		self.PL[game] = PlayerList(game)
		self.DA[game] = DroneAvailability(game)
		self.save()


	def cleanGames(self):
		for id in self.DP.keys():
			if id not in Game.ids():
				del self.DP[id]
				del self.ML[id]
				del self.PL[id]
				del self.DA[id]
		self.save()