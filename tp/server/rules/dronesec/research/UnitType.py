"""Unit Type Researches"""
from tp.server.rules.dronesec.bases.Research import Research

class UnitType(Research):
	"""
	Unit Researches add new drones to the list of avaiable drones.
	"""
	attributes = {\
		'ship': Research.Attribute('ship', '', 'private'),
		}
