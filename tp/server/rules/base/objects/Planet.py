
from sbases.Object import Object

class Planet(Object):
	attributes = { \
		'owner': Object.Attribute('owner', -1, 'public')
	}

Planet.typeno = 3
Object.types[Planet.typeno] = Planet
