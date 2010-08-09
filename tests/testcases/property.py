from test import TestSuite
from common import ( AuthorizedTestSession, Expect, TestSessionUtils,
		ConnectedTestSession, GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged )

from tp.server.model import DatabaseManager

class GetPropertyWhenNotLogged( GetWithIDWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetProperty request? """

	__request__ = 'GetProperty'

class GetPropertyIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetPropertyIDs request? """

	__request__ = 'GetPropertyIDs'

class PropertiesTestSuite( TestSuite ):
	""" Performs all tests related to GetProperty and GetPropertyIDs requests. """
	__name__  = 'Properties'
	__tests__ = [ GetPropertyWhenNotLogged, GetPropertyIDsWhenNotLogged ]

	def setUp( self ):
		game = self.ctx['game']

		Property = game.objects.use( 'Property' )

		self.ctx['properties'] = []

		with DatabaseManager().session() as session:
			for p in self.ctx['properties']:
				session.add( p )
	
	def tearDown( self ):
		with DatabaseManager().session() as session:
			for p in self.ctx['properties']:
				p.remove( session )

__tests__ = [ PropertiesTestSuite ]
