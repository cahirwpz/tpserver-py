
from sbases.Object import Object

class Planet(Object):
	attributes = { \
		'owner': Object.Attribute('owner', -1, 'public')
	}
	orderclasses = ('sorders.NOp', 'sorders.BuildFleet')

Planet.typeno = 3
Object.types[Planet.typeno] = Planet
