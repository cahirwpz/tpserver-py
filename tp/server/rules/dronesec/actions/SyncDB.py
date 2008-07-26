#This file should try to sync the DB with the current version of the csv file given

from tp.server.rules.dronesec.research.MasterList import MasterList

def do(top):
	MasterList.syncCombatType()
