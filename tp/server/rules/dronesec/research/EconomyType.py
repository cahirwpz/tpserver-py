
from tp.server.rules.dronesec.bases.Research import Research

class EconomyType(Research):
	resources = 0
	research = 0
	researchType = 0
	resourcesRatio = 0
	researchRatio = 0
	attributes = {\
		'resources': Research.Attribute('resources', 0, 'private'),
		'research': Research.Attribute('research', 0, 'private'),
		'researchType': Research.Attribute('researchType', 0, 'private'),
		'resourcesRatio': Research.Attribute('resourcesRatio', 0, 'private'),
		'researchRatio': Research.Attribute('researchRatio', 0, 'private'),
	}