
from tp.server.rules.dronesec.bases.Research import Research

class CombatType(Research):

	attributes = {\
		'damage': Research.Attribute('damage', 0, 'private'),
		'numAttacks': Research.Attribute('numAttacks', 0, 'private'),
		'health': Research.Attribute('health', 0, 'private'),
		'types': Research.Attribute('types', 0, 'private'),
		'ships': Research.Attribute('ships', 0, 'private'),
		}
