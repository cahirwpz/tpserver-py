from test import TestSuite
from common import AuthorizedTestSession, Expect
from templates import GetWithIDWhenNotLogged, GetIDSequenceWhenNotLogged, WhenNotLogged

from tp.server.model import DatabaseManager

class GetExistingDesign( AuthorizedTestSession ):#{{{
	""" Does server respond properly if asked about existing board? """

	def __iter__( self ):
		design = self.ctx['designs'][1]

		GetDesign = self.protocol.use( 'GetDesign' )

		packet = yield GetDesign( self.seq, [ design.id ] ), Expect( 'Design' )

		assert packet.id == design.id, \
			"Server responded with different DesignId than requested!"
#}}}

class GetNonExistentDesign( AuthorizedTestSession ):#{{{
	""" Does server fail to respond if asked about nonexistent board? """

	def __iter__( self ):
		design = self.ctx['designs'][1]

		GetDesign = self.protocol.use( 'GetDesign' )

		packet = yield GetDesign( self.seq, [ design.id + 666 ] ), Expect( 'Design', ('Fail', 'NoSuchThing') )

		assert packet.type != 'Design', \
			"Server does return information for non-existent DesignId = %s!" % ( design.id + 666 )
#}}}

class GetMultipleDesigns( AuthorizedTestSession ):#{{{
	""" Does server return sequence of Design packets if asked about two boards? """

	def __iter__( self ):
		d1 = self.ctx['designs'][2]
		d2 = self.ctx['designs'][0]

		GetDesign = self.protocol.use( 'GetDesign' )

		s, p1, p2 = yield GetDesign( self.seq, [ d1.id, d2.id ] ), Expect( ('Sequence', 2, 'Design' ) )

		assert p1.id == d1.id and p2.id == d2.id, \
			"Server returned different DesignIds (%d,%d) than requested (%d,%d)." % (p1.id, p2.id, d1.id, d2.id)
#}}}

class GetDesignWhenNotLogged( GetWithIDWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetDesign request? """

	__request__ = 'GetDesign'
#}}}

class GetDesignIDsWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got GetDesignIds request? """

	__request__ = 'GetDesignIDs'
#}}}

class AddDesignWhenNotLogged( WhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got AddDesign request? """

	__request__ = 'AddDesign'

	def makeRequest( self, AddDesign ):
		return AddDesign( self.seq, 0, 0, [], "Design", "Design used for testing purposes", 0, 0, [], "foobar", [] )
#}}}

class ModifyDesignWhenNotLogged( WhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got ModifyDesign request? """

	__request__ = 'ModifyDesign'

	def makeRequest( self, ModifyDesign ):
		return ModifyDesign( self.seq, 0, 0, [], "Design", "Design used for testing purposes", 0, 0, [], "foobar", [] )
#}}}

class RemoveDesignWhenNotLogged( GetIDSequenceWhenNotLogged ):#{{{
	""" Does a server respond properly when player is not logged but got RemoveDesign request? """

	__request__ = 'RemoveDesign'
#}}}

class DesignTestSuite( TestSuite ):#{{{
	__name__  = 'Designs'
	__tests__ = [ GetDesignWhenNotLogged, GetDesignIDsWhenNotLogged,
			AddDesignWhenNotLogged, RemoveDesignWhenNotLogged,
			ModifyDesignWhenNotLogged, GetExistingDesign, GetNonExistentDesign,
			GetMultipleDesigns ]

	def setUp( self ):
		game = self.ctx['game']

		Design = game.objects.use( 'Design' )

		scout = Design(
			name        = "Scout",
			description = "A fast light ship with advanced sensors.",
			categories  = [],
			components  = [] )

		frigate = Design(
			name         = "Frigate",
			description  = "A general purpose ship with weapons and ability to colonise new planets.",
			categories  = [],
			components  = [] )

		battleship = Design(
			name        = "Battleship",
			description = "A heavy ship who's main purpose is to blow up other ships.",
			categories  = [],
			components  = [] )

		self.ctx['designs'] = [ scout, frigate, battleship ]

		with DatabaseManager().session() as session:
			for design in self.ctx['designs']:
				session.add( design )
	
	def tearDown( self ):
		with DatabaseManager().session() as session:
			for design in self.ctx['designs']:
				design.remove( session )
#}}}

__tests__ = [ DesignTestSuite ]
