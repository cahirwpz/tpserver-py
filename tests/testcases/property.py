from test import TestSuite
from templates import GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged

from tp.server.model import Model

class GetPropertyWhenNotLogged( GetWithIDWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetProperty request? """

	__request__ = 'GetProperty'
#}}}

class GetPropertyIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetPropertyIDs request? """

	__request__ = 'GetPropertyIDs'
#}}}

class PropertiesTestSuite( TestSuite ):#{{{
	""" Performs all tests related to GetProperty and GetPropertyIDs requests. """
	__name__  = 'Properties'
	__tests__ = [ GetPropertyWhenNotLogged, GetPropertyIDsWhenNotLogged ]

	def setUp( self ):
		game = self.ctx['game']

		Property = game.objects.use( 'Property' )

		self.ctx['properties'] = []

		Model.add( *self.ctx['properties'] )
	
	def tearDown( self ):
		Model.remove( *self.ctx['properties'] )
#}}}

__tests__ = [ PropertiesTestSuite ]
