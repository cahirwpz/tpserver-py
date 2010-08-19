from templates import GetWithIDSlotWhenNotLogged, GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged, WhenNotLogged
from testenv import GameTestEnvMixin

from tp.server.model import Model

class OrderTestEnvMixin( GameTestEnvMixin ):
	def setUp( self ):
		Order = self.model.use( 'Order' )

		self.orders = []

		Model.add( self.orders )
	
	def tearDown( self ):
		Model.remove( self.orders )

class GetOrderWhenNotLogged( GetWithIDSlotWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetOrder request? """

	__request__ = 'GetOrder'

class GetOrderDescWhenNotLogged( GetWithIDWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetOrderDesc request? """

	__request__ = 'GetOrderDesc'

class GetOrderDescIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetOrderDescIDs request? """

	__request__ = 'GetOrderDescIDs'

class OrderInsertWhenNotLogged( WhenNotLogged ):
	""" Does a server respond properly when player is not logged but got OrderInsert request? """

	__request__ = 'OrderInsert'

	def makeRequest( self, OrderInsert ):
		return OrderInsert( self.seq, 1, 1, 1, 1, [] )

class OrderProbeWhenNotLogged( WhenNotLogged ):
	""" Does a server respond properly when player is not logged but got OrderProbe request? """

	__request__ = 'OrderProbe'

	def makeRequest( self, OrderProbe ):
		return OrderProbe( self.seq, 1, 1, 1, 1, [] )

class RemoveOrderWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got RemoveOrder request? """

	__request__ = 'RemoveOrder'

__all__ = [ 'GetOrderWhenNotLogged', 
			'GetOrderDescWhenNotLogged', 
			'GetOrderDescIDsWhenNotLogged', 
			'OrderInsertWhenNotLogged', 
			'OrderProbeWhenNotLogged', 
			'RemoveOrderWhenNotLogged' ]
