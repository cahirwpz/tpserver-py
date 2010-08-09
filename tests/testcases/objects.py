from test import TestSuite
from common import AuthorizedTestSession, Expect
from templates import GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged, WhenNotLogged

from tp.server.model import DatabaseManager, Vector3D

class GetEmptyObjectList( AuthorizedTestSession ):#{{{
	""" Sends empty list of ObjectIDs. """

	def __iter__( self ):
		GetObjectsByID = self.protocol.use( 'GetObjectsByID' )

		yield GetObjectsByID( self.seq, [] ), Expect( ('Fail', 'Protocol') )
#}}}

class GetObjectIds( AuthorizedTestSession ):#{{{
	""" Sends some random Object related requests. """

	def __iter__( self ):
		GetObjectIDs, GetObjectsByID = self.protocol.use( 'GetObjectIDs', 'GetObjectsByID' )

		response = yield GetObjectIDs( self.seq, -1, 0, 0, -1 ), Expect( 'ObjectIDs' )
		response = yield GetObjectIDs( self.seq, -1, 0, response.remaining, -1 ), Expect( 'ObjectIDs' )

		yield GetObjectsByID( self.seq, [ id for id, modtime in response.modtimes ] )
#}}}

class GetObjectsByIDWhenNotLogged( GetWithIDWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetObjectsByID request? """

	__request__ = 'GetObjectsByID'
#}}}

class GetObjectIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetObjectIDs request? """

	__request__ = 'GetObjectIDs'
#}}}

class GetObjectIDsByContainerWhenNotLogged( WhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetObjectIDsByContainer request? """

	__request__ = 'GetObjectIDsByContainer'

	def makeRequest( self, GetObjectIDsByContainer ):
		return GetObjectIDsByContainer( self.seq, 0 )
#}}}

class GetObjectIDsByPosWhenNotLogged( WhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetObjectIDsByPos request? """

	__request__ = 'GetObjectIDsByPos'

	def makeRequest( self, GetObjectIDsByPos ):
		return GetObjectIDsByPos( self.seq, ( 0, 0, 0 ), 1000 )
#}}}

class GetObjectsByPosWhenNotLogged( WhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetObjectsByPos request? """

	__request__ = 'GetObjectsByPos'

	def makeRequest( self, GetObjectsByPos ):
		return GetObjectsByPos( self.seq, ( 0, 0, 0 ), 1000 )
#}}}

class ObjectTestSuite( TestSuite ):#{{{
	__name__  = 'Objects'
	__tests__ = [ GetObjectsByIDWhenNotLogged, GetObjectIDsWhenNotLogged,
			GetObjectIDsByContainerWhenNotLogged,
			GetObjectIDsByPosWhenNotLogged, GetObjectsByPosWhenNotLogged,
			GetEmptyObjectList, GetObjectIds ]

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
#}}}

__tests__ = [ ObjectTestSuite ]
