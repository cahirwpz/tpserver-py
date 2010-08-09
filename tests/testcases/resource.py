from test import TestSuite
from common import ( AuthorizedTestSession, Expect, TestSessionUtils,
		ConnectedTestSession, GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged )

from tp.server.model import DatabaseManager

class GetResourceWhenNotLogged( GetWithIDWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetResource request? """

	__request__ = 'GetResource'

class GetResourceIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetResourceIDs request? """

	__request__ = 'GetResourceIDs'

class ResourcesTestSuite( TestSuite ):
	""" Performs all tests related to GetResource and GetResourceIDs requests. """
	__name__  = 'Resources'
	__tests__ = [ GetResourceWhenNotLogged, GetResourceIDsWhenNotLogged ]

	def setUp( self ):
		game = self.ctx['game']

		ResourceType = game.objects.use( 'ResourceType' )

		self.ctx['resources'] = []

		with DatabaseManager().session() as session:
			for p in self.ctx['resources']:
				session.add( p )
	
	def tearDown( self ):
		with DatabaseManager().session() as session:
			for p in self.ctx['resources']:
				p.remove( session )

__tests__ = [ ResourcesTestSuite ]
