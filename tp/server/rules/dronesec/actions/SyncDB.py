"""
Synchronizes the Research SQL Database with the CSV files
"""
from tp.server.rules.dronesec.research.MasterList import MasterList

def do(top):
	"""
	Action Method for SyncDB
	
	Research Database tables are synchronized with the csv files.
	
	Note: Designs for Researches are not synchronized at this time
	"""
	MasterList.syncCombatType()
	MasterList.syncEconomyType()
	MasterList.syncWorldType()