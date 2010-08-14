from test import TestSuite
from common import AuthorizedTestSession, ExpectFail
from templates import GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged, WhenNotLogged, GetItemsWithID, GetWithIDMixin, GetItemIDs

from tp.server.model import Model, Vector3D

class GetObjectMixin( GetWithIDMixin ):#{{{
	__request__  = 'GetObjectsByID'
	__response__ = 'Object'

	__attrs__   = [ 'id', 'name', 'size' ]
	__attrmap__ = {}
	__attrfun__ = [ 'modtime', 'position', 'velocity', 'contains', 'ordertypes', 'otype' ]

	def convert_position( self, packet, obj ):
		return ( Vector3D( packet.pos[0], packet.pos[1], packet.pos[2] ), obj.position )

	def convert_velocity( self, packet, obj ):
		return ( Vector3D( packet.vel[0], packet.vel[1], packet.vel[2] ), Vector3D(0,0,0) )

	def convert_contains( self, packet, obj ):
		return ( [ child for child in packet.contains ], [ child.id for child in obj.children ] )

	def convert_ordertypes( self, packet, obj ):
		return ( [ order for order in packet.ordertypes ], [ order_object.order_type_id for order_object in obj.type.order_types ] )

	def convert_otype( self, packet, obj ):
		return ( packet.otype, obj.type.id )
#}}}

class GetEmptyObjectList( AuthorizedTestSession ):#{{{
	""" Sends empty list of ObjectIDs. """

	def __iter__( self ):
		GetObjectsByID = self.protocol.use( 'GetObjectsByID' )

		yield GetObjectsByID( self.seq, [] ), ExpectFail('Protocol')
#}}}

class GetAllObjects( GetItemsWithID, GetObjectMixin ):#{{{
	""" Does server return sequence of Resource packets if asked about all objects? """

	@property
	def items( self ):
		return self.ctx['objects']
#}}}

class GetObjectIDs( GetItemIDs ):#{{{
	""" Does server return the IDs of all available Objects? """

	__request__  = 'GetObjectIDs'
	__response__ = 'ObjectIDs'
	__object__   = 'Object'

	@property
	def items( self ):
		return self.ctx['objects']
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
			GetEmptyObjectList, GetAllObjects, GetObjectIDs ]

	def setUp( self ):
		game = self.ctx['game']

		Universe, StarSystem, Planet, Fleet = self.model.use( 'Universe', 'StarSystem', 'Planet', 'Fleet' )

		universe = Universe(
				name = "The Universe",
				size = 10**8,
				age  = 0 )

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

		fleet = Fleet(
				parent   = planet,
				size     = 3,
				name     = "The Fleet",
				ships    = [],
				damage   = 0,
				position = planet.position,
				owner    = self.ctx['players'][0])

		self.ctx['objects'] = [ universe, system, planet, fleet ]

		Model.add( self.ctx['objects'] )
	
	def tearDown( self ):
		Model.remove( self.ctx['objects'] )
#}}}

__tests__ = [ ObjectTestSuite ]
