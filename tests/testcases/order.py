from test import TestSuite
from templates import GetWithIDSlotWhenNotLogged, GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged, WhenNotLogged

from tp.server.model import Model

class GetOrderWhenNotLogged( GetWithIDSlotWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetOrder request? """

	__request__ = 'GetOrder'
#}}}

class GetOrderDescWhenNotLogged( GetWithIDWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetOrderDesc request? """

	__request__ = 'GetOrderDesc'
#}}}

class GetOrderDescIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetOrderDescIDs request? """

	__request__ = 'GetOrderDescIDs'
#}}}

class OrderInsertWhenNotLogged( WhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got OrderInsert request? """

	__request__ = 'OrderInsert'

	def makeRequest( self, OrderInsert ):
		return OrderInsert( self.seq, 1, 1, 1, 1, [] )
#}}}

class OrderProbeWhenNotLogged( WhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got OrderProbe request? """

	__request__ = 'OrderProbe'

	def makeRequest( self, OrderProbe ):
		return OrderProbe( self.seq, 1, 1, 1, 1, [] )
#}}}

class RemoveOrderWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got RemoveOrder request? """

	__request__ = 'RemoveOrder'
#}}}

class OrdersTestSuite( TestSuite ):#{{{
	""" Performs all tests related to GetOrder and GetOrderIDs requests. """
	__name__  = 'Orders'
	__tests__ = [ GetOrderWhenNotLogged, GetOrderDescWhenNotLogged,
			GetOrderDescIDsWhenNotLogged, OrderInsertWhenNotLogged,
			OrderProbeWhenNotLogged, RemoveOrderWhenNotLogged ]

	def setUp( self ):
		game = self.ctx['game']

		Order = game.objects.use( 'Order' )

		self.ctx['orders'] = []

		Model.add( *self.ctx['orders'] )
	
	def tearDown( self ):
		Model.remove( *self.ctx['orders'] )
#}}}

__tests__ = [ OrdersTestSuite ]
