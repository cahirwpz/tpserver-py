
from tpserver.bases.Object import Object

class Universe(Object):
	attributes = {'turn': Object.Attribute('turn', 0, 'public')}

Universe.typeno = 0
Object.types[Universe.typeno] = Universe
