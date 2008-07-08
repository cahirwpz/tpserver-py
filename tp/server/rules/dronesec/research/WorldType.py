
from tp.server.rules.dronesec.bases.Research import Research

class WorldType(Research):
##	speed = 0
##	speedRatio = 0
##	units = None
##	type = None
##	abilities = None
##	power = 0
	attributes = {\
		'speed': Research.Attribute('speed', 0, 'private'),
		'speedRatio': Research.Attribute('speedRatio', 0, 'private'),
		'power': Research.Attribute('power', 0, 'private'),
		'units': Research.Attribute('units', '', 'private'),
		'types': Research.Attribute('types', '', 'private'),
		}