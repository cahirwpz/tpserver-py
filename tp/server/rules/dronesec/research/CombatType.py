"""Combat Type Researches"""
from tp.server.rules.dronesec.bases.Research import Research

class CombatType(Research):
	"""
	Combat Researches affect a drone's combat capabilities.
	"""
	attributes = {\
		'damage': Research.Attribute('damage', 0, 'private'),
		'numAttacks': Research.Attribute('numAttacks', 0, 'private'),
		'health': Research.Attribute('health', 0, 'private'),
		'strength': Research.Attribute('strength', '', 'private'),
		'weakness': Research.Attribute('weakness', '', 'private'),
		'types': Research.Attribute('types', 0, 'private'),
		'ships': Research.Attribute('ships', 0, 'private'),
		}
