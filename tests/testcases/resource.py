from test import TestSuite
from templates import GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged, GetItemsWithID, GetWithIDMixin, GetItemIDs

from tp.server.model import Model

class GetResourceMixin( GetWithIDMixin ):
	__request__  = 'GetResource'
	__response__ = 'Resource'

	__attrs__ = [ 'id', 'description', 'modtime', 'weight', 'size' ]

	__attrmap__ = dict(
			singularname     = 'name_singular',
			pluralname       = 'name_plural',
			singularunitname = 'unit_singular',
			pluralunitname   = 'unit_plural' )

	__attrfun__ = [ 'modtime' ]

class GetResourceWhenNotLogged( GetWithIDWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetResource request? """

	__request__ = 'GetResource'

class GetAllResources( GetItemsWithID, GetResourceMixin ):
	""" Does server return sequence of Resource packets if asked about all resources? """

	@property
	def items( self ):
		return reversed( self.ctx['resources'] )

class GetResourceIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):
	""" Does a server respond properly when player is not logged but got GetResourceIDs request? """

	__request__ = 'GetResourceIDs'

class GetAllResourceIDs( GetItemIDs ):
	""" Does server return the IDs of all available Resources? """

	__request__  = 'GetResourceIDs'
	__response__ = 'ResourceIDs'
	__object__   = 'Resource'

	@property
	def items( self ):
		return self.ctx['resources']

class ResourcesTestSuite( TestSuite ):
	""" Performs all tests related to GetResource and GetResourceIDs requests. """
	__name__  = 'Resources'
	__tests__ = [ GetResourceWhenNotLogged, GetAllResources, GetResourceIDsWhenNotLogged, GetAllResourceIDs ]

	def setUp( self ):
		game = self.ctx['game']

		ResourceType = self.model.use( 'ResourceType' )

		hq = ResourceType(
				id            = 9,
				name_singular = "Headquarters",
				description   = "The famous headquarters for a big trading conglomerate." )

		credit = ResourceType(
				id            = 3,
				name_singular = "Credit",
				name_plural   = "Credits",
				description   = "The root of all evil, money." )

		uranium = ResourceType(
				id            = 7,
				name_singular = "Uranium",
				name_plural   = "Uranium",
				unit_singular = "kt",
				unit_plural   = "kt",
				description   = "A heavy metal used in weapons.",
				weight        = 1,
				size          = 1 )

		weapon = ResourceType(
				id            = 4,
				name_singular = "Weapon",
				name_plural   = "Weapons",
				unit_singular = "part",
				unit_plural   = "parts",
				description   = "A ship component for destroying other ships.",
				weight        = 1,
				size          = 1 )

		self.ctx['resources'] = [ hq, credit, uranium, weapon ]

		Model.add( self.ctx['resources'] )
	
	def tearDown( self ):
		Model.remove( self.ctx['resources'] )

__tests__ = [ ResourcesTestSuite ]
