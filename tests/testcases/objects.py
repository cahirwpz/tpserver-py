from test import TestSuite
from common import AuthorizedTestSession, Expect

from tp.server.model import DatabaseManager, Vector3D

class GetEmptyObjectList( AuthorizedTestSession ):
	""" Sends empty list of ObjectIDs. """

	NoFailAllowed = False

	def __iter__( self ):
		GetObjectsByID = self.protocol.use( 'GetObjectsByID' )

		yield GetObjectsByID( self.seq, [] ), Expect( ('Fail', 'Protocol') )

class GetObjectIds( AuthorizedTestSession ):
	""" Sends some random Object related requests. """

	def __iter__( self ):
		GetObjectIDs, GetObjectsByID = self.protocol.use( 'GetObjectIDs', 'GetObjectsByID' )

		response = yield GetObjectIDs( self.seq, -1, 0, 0, -1 )
		response = yield GetObjectIDs( self.seq, -1, 0, response.remaining, -1 )

		yield GetObjectsByID( self.seq, [ id for id, modtime in response.modtimes ] )

class ObjectTestSuite( TestSuite ):
	__name__  = 'Objects'
	__tests__ = [ GetEmptyObjectList, GetObjectIds ]

	def setUp( self ):
		game = self.ctx['game']

		Universe, StarSystem, Planet = game.objects.use( 'Universe', 'StarSystem',	'Planet' )

		universe = Universe( name = "The Universe", size = 10**8, age = 0 )

		system = StarSystem(
				name		= "The Star System",
				parent		= universe,
				position	= Vector3D( 0, 0, 0 ),
				size		= 10**4)

		planet = Planet(
				name		= "The Planet",
				parent		= system,
				position	= Vector3D( system.position.x + 5,
										system.position.y + 7 ),
				size		= 10**2,
				owner		= self.ctx['players'][0] )

		self.ctx['objects'] = [ universe, system, planet ]

		with DatabaseManager().session() as session:
			for obj in self.ctx['objects']:
				session.add( obj )
	
	def tearDown( self ):
		with DatabaseManager().session() as session:
			for obj in self.ctx['objects']:
				obj.remove( session )

__tests__ = [ ObjectTestSuite ]
