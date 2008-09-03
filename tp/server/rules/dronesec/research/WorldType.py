"""World Type Researches"""
from tp.server.rules.dronesec.bases.Research import Research

class WorldType(Research):
	"""
	World Researches affect how fast fleets move and their capturing ability.
	"""
	attributes = {\
		'speed': Research.Attribute('speed', 0, 'private'),
		'speedRatio': Research.Attribute('speedRatio', 0, 'private'),
		'power': Research.Attribute('power', 0, 'private'),
		'units': Research.Attribute('units', '', 'private'),
		'types': Research.Attribute('types', '', 'private'),
		}