
from tp.server.bases.Object import Object

class System(Object):
	attributes = {}

System.typeno = 2
Object.types[System.typeno] = System
