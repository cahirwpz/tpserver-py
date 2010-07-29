from common import AuthorizedTestSession, Expect

class GetExistingDesign( AuthorizedTestSession ):
	""" Does server respond properly if asked about existing board? """

	def __iter__( self ):
		GetDesign = self.protocol.use( 'GetDesign' )

		packet = yield GetDesign( self.seq, [1] ), Expect( 'Design' )

		if packet.id != 1:
			self.failed( "Server responded with different DesignId than requested!" )

class GetNonExistentDesign( AuthorizedTestSession ):
	""" Does server fail to respond if asked about nonexistent board? """

	NoFailAllowed = False
	WrongDesignId = 666

	def __iter__( self ):
		GetDesign = self.protocol.use( 'GetDesign' )

		packet = yield GetDesign( self.seq, [self.WrongDesignId] ), Expect( 'Design', ('Fail', 'NoSuchThing') )

		if packet.type == 'Design':
			self.failed( "Server does return information for non-existent DesignId = %s!" % self.WrongDesignId )

class GetMultipleDesigns( AuthorizedTestSession ):
	""" Does server return sequence of Design packets if asked about two boards? """

	def __iter__( self ):
		GetDesign = self.protocol.use( 'GetDesign' )

		s, p1, p2 = yield GetDesign( self.seq, [1, 2] ), Expect( ('Sequence', 2, 'Design' ) )

		if p1.id != 1 or p2.id != 2:
			self.failed( "Server returned different DesignIds (%d,%d) than requested (1,2)." % (p1.id, p2.id) )

__tests__ = [ GetExistingDesign, GetNonExistentDesign, GetMultipleDesigns ]
