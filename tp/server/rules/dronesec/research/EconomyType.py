
from tp.server.rules.dronesec.bases.Research import Research

class EconomyType(Research):
	attributes = {\
		'resources': Research.Attribute('resources', 0, 'private'),
		'resourcesRatio': Research.Attribute('resourcesRatio', 0, 'private'),
		'researchRatio': Research.Attribute('researchRatio', 0, 'private'),
		'researchType': Research.Attribute('researchType', 0, 'private'),
		'droneCost': Research.Attribute('droneCost', 0, 'private'),
		'droneRatio': Research.Attribute('droneRatio', 0, 'private'),
		'droneTypes': Research.Attribute('droneTypes', '', 'private'),
		'droneShips': Research.Attribute('droneShips', '', 'private'),
	}