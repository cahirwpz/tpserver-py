from test import TestSuite
from templates import GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged

from tp.server.model import DatabaseManager

class GetComponentWhenNotLogged( GetWithIDWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetComponent request? """

	__request__ = 'GetComponent'
#}}}

class GetComponentIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetComponentIDs request? """

	__request__ = 'GetComponentIDs'
#}}}

class ComponentsTestSuite( TestSuite ):#{{{
	""" Performs all tests related to GetComponent and GetComponentIDs requests. """
	__name__  = 'Components'
	__tests__ = [ GetComponentWhenNotLogged, GetComponentIDsWhenNotLogged ]

	def setUp( self ):
		game = self.ctx['game']

		Component = game.objects.use( 'Component' )

		self.ctx['components'] = []

		with DatabaseManager().session() as session:
			for p in self.ctx['components']:
				session.add( p )
	
	def tearDown( self ):
		with DatabaseManager().session() as session:
			for p in self.ctx['components']:
				p.remove( session )
#}}}

__tests__ = [ ComponentsTestSuite ]
