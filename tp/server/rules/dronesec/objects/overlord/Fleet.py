###Overlord Fleet
from sqlalchemy import *

from types import TupleType, ListType

from tp.server.bases.Object import Object
from tp.server.bases.Design import Design
from tp.server.rules.dronesec.objects.Fleet import Fleet as Fleetbase
from Messenger import Messenger as Jarvis

class Fleet(Fleetbase):
	attributes = { \
		'owner': Object.Attribute('owner', -1, 'public'),
		'ships': Object.Attribute('ships', {}, 'protected'),
		'damage': Object.Attribute('damage', 0, 'protected'),
		'pos' : Object.Attribute('pos', (0,0,0), 'private'),
		'command' : Object.Attribute('command', 0, 'private'),
	}

	##Commands:
	## 0 : Stop
	## 1 : Attract
	## 2 : Repel

	orderclasses = (
		'tp.server.rules.base.orders.NOp',
		'tp.server.rules.dronesec.orders.Move',
		'tp.server.rules.dronesec.orders.Attract',
		'tp.server.rules.dronesec.orders.Repel',
		'tp.server.rules.dronesec.orders.Stop',
		)

	ship_types = {0: 'Overlord'}
	ship_hp     = {0: 10000}
	ship_damage = {0:0}
	ship_speed  = {0: 700}

	#############################################
	# Movement functions
	#############################################
	def speed(self):
		"""\
		Returns the maximum speed of the fleet.
		"""
		return self.ship_speed[0]

	def ghost(self):
		"""\
		Overlords don't die
		"""
		return False


Fleet.typeno = 4
Object.types[Fleet.typeno] = Fleet
