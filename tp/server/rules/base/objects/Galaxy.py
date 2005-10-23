
from tp.server.bases.Object import Object

class Galaxy(Object):
	attributes = {}

Galaxy.typeno = 1
Object.types[Galaxy.typeno] = Galaxy
