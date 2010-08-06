from test import TestSuite
from common import AuthorizedTestSession, Expect

from tp.server.model import DatabaseManager

class GetExistingDesign( AuthorizedTestSession ):
	""" Does server respond properly if asked about existing board? """

	def __iter__( self ):
		design = self.ctx['designs'][1]

		GetDesign = self.protocol.use( 'GetDesign' )

		packet = yield GetDesign( self.seq, [ design.id ] ), Expect( 'Design' )

		if packet.id != design.id:
			self.failed( "Server responded with different DesignId than requested!" )

class GetNonExistentDesign( AuthorizedTestSession ):
	""" Does server fail to respond if asked about nonexistent board? """

	NoFailAllowed = False

	def __iter__( self ):
		design = self.ctx['designs'][1]

		GetDesign = self.protocol.use( 'GetDesign' )

		packet = yield GetDesign( self.seq, [ design.id + 666 ] ), Expect( 'Design', ('Fail', 'NoSuchThing') )

		if packet.type == 'Design':
			self.failed( "Server does return information for non-existent DesignId = %s!" % ( design.id + 666 ) )

class GetMultipleDesigns( AuthorizedTestSession ):
	""" Does server return sequence of Design packets if asked about two boards? """

	def __iter__( self ):
		d1 = self.ctx['designs'][2]
		d2 = self.ctx['designs'][0]

		GetDesign = self.protocol.use( 'GetDesign' )

		s, p1, p2 = yield GetDesign( self.seq, [ d1.id, d2.id ] ), Expect( ('Sequence', 2, 'Design' ) )

		if p1.id != d1.id or p2.id != d2.id:
			self.failed( "Server returned different DesignIds (%d,%d) than requested (%d,%d)." % (p1.id, p2.id, d1.id, d2.id) )

class DesignTestSuite( TestSuite ):
	__name__  = 'Designs'
	__tests__ = [ GetExistingDesign, GetNonExistentDesign, GetMultipleDesigns ]

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

__tests__ = [ DesignTestSuite ]
