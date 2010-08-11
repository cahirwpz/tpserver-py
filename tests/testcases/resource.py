from test import TestSuite
from templates import GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged

from tp.server.model import Model

class GetResourceWhenNotLogged( GetWithIDWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetResource request? """

	__request__ = 'GetResource'
#}}}

class GetResourceIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetResourceIDs request? """

	__request__ = 'GetResourceIDs'
#}}}

class ResourcesTestSuite( TestSuite ):#{{{
	""" Performs all tests related to GetResource and GetResourceIDs requests. """
	__name__  = 'Resources'
	__tests__ = [ GetResourceWhenNotLogged, GetResourceIDsWhenNotLogged ]

	def setUp( self ):
		game = self.ctx['game']

		ResourceType = game.objects.use( 'ResourceType' )

		self.ctx['resources'] = []

		Model.add( *self.ctx['resources'] )
	
	def tearDown( self ):
		Model.remove( *self.ctx['resources'] )
#}}}

__tests__ = [ ResourcesTestSuite ]
