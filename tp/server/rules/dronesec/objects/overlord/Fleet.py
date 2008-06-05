
from sqlalchemy import *

from types import TupleType, ListType

from tp.server.bases.Object import Object
from tp.server.bases.Design import Design
from tp.server.rules.dronesec.objects.Fleet import Fleet as Fleetbase

class Fleet(Fleetbase):
	orderclasses = (
		'tp.server.rules.base.orders.NOp',
		'tp.server.rules.minisec.orders.Move',
		)


	ship_types = {0: 'Overlord'}
	ship_hp     = {0: 10000}
	ship_damage = {0:0}
	ship_speed  = {0: 1000000000}

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
