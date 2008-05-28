
from sqlalchemy import *

from types import TupleType, ListType

import os
from tp.server.bases.Object import Object
from tp.server.bases.Design import Design
from tp.server.bases.Combattant import Combattant
from tp.server.rules.dronesec.drones.Dronepedia import Dronepedia


class Drone(Object, Combattant):
	attributes = {
		'owner': Object.Attribute('owner', -1, 'public'),
		'damage': Object.Attribute('damage', {}, 'protected'),
	}

	orderclasses = ('tp.server.rules.base.orders.NOp',
					'tp.server.rules.minisec.orders.Move',
					'tp.server.rules.minisec.orders.SplitFleet',
					'tp.server.rules.base.orders.MergeFleet',
					'tp.server.rules.base.orders.Colonise')

	DP = Dronepedia()

	def fn_ships(self, value=None):
		if value == None:
			return self.DP.name.items()
Drone.typeno = 4
Object.types[Drone.typeno] = Drone
