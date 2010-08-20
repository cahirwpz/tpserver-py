from common import TestSession

class IncrementingSequenceMixin( object ):
	@property
	def seq( self ):
		try:
			self.__seq += 1
		except AttributeError:
			self.__seq = 1
		
		return self.__seq

class ConnectedTestSession( TestSession, IncrementingSequenceMixin ):
	def __init__( self, *args, **kwargs ):
		super( ConnectedTestSession, self ).__init__( *args, **kwargs )

		self.scenarioList.append( self.__connect() )

	def __connect( self ):
		Connect = self.protocol.use( 'Connect' )

		response = yield Connect( self.seq, "tpserver-tests client" )

		self.assertPacket( response, 'Okay' )

class AuthorizedTestSession( TestSession, IncrementingSequenceMixin ):
	def __init__( self, *args, **kwargs ):
		super( AuthorizedTestSession, self ).__init__( *args, **kwargs )

		self.scenarioList.append( self.__login() )
	
	def __login( self ):
		Connect, Login = self.protocol.use( 'Connect', 'Login' )

		response = yield Connect( self.seq, "tpserver-tests client" )

		self.assertPacket( response, 'Okay' )

		response = yield Login( self.seq, "%s@%s" % ( self.sign_in_as.username, self.game.name ), self.sign_in_as.password )

		self.assertPacket( response, 'Okay' )

class GetWithIDWhenNotLogged( ConnectedTestSession ):
	__request__ = None

	def __iter__( self ):
		Request = self.protocol.use( self.__request__ )

		response = yield Request( self.seq, [1] )

		self.assertPacketFail( response, 'UnavailableTemporarily' )

class WhenNotLogged( ConnectedTestSession ):
	__request__ = None

	def __iter__( self ):
		RequestType = self.protocol.use( self.__request__ )

		response = yield self.makeRequest( RequestType )

		self.assertPacketFail( response, 'UnavailableTemporarily' )

class GetWithIDSlotWhenNotLogged( WhenNotLogged ):
	def makeRequest( self, GetWithID ):
		return GetWithID( self.seq, 1, [1] )

class GetIDSequenceWhenNotLogged( ConnectedTestSession ):
	def makeRequest( self, IDSequence ):
		return IDSequence( self.seq, -1, 0, -1 )

class WithIDTestMixin( object ):
	def convert_modtime( self, packet, obj ):
		return packet.modtime, self.datetimeToInt( obj.mtime )

	def getFail( self, item ):
		pass

	def assertPacketEqual( self, packet, obj ):
		attrs = self.__attrs__ + list( self.__attrmap__ ) + self.__attrfun__

		for attr in attrs:
			if attr in self.__attrfun__:
				pval, oval = getattr( self, 'convert_%s' % attr )( packet, obj )
			else:
				objattr = self.__attrmap__.get( attr, attr )

				pval = getattr( packet, attr )
				oval = getattr( obj, objattr )

			self.assertEqual( pval, oval,
					"Server responded with different %s(%d).%s (%s) than expected (%s)!" % ( self.__response__, packet.id, attr, pval, oval ) )

	def assertPacketSeqEqual( self, sequence, objs ):
		for packet, obj in zip( sequence[1:], objs ):
			if not self.getFail( obj ):
				self.assertPacketEqual( packet, obj )

class GetItemWithID( AuthorizedTestSession ):
	"""
	Must provide two class attributes:
	__request__  name of a request
	__response__ name of a expected response
	"""

	@property
	def item( self ):
		raise NotImplementedError

	@property
	def items( self ):
		return [ self.item ]

	def getId( self, item ):
		return item.id

	def __iter__( self ):
		Request = self.protocol.use( self.__request__ )

		items = list( self.items )

		response = yield Request( self.seq, [ self.getId( item ) for item in items ] )

		if isinstance( response, list ):
			packets = response[1:]
		else:
			packets = [ response ]

		for item, packet in zip( items, packets ):
			fail = self.getFail( item )

			if fail:
				if fail == 'NoSuchThing':
					msg  = "Server does return information for non-existent %s.Id (%s)!" % ( self.__response__, self.getId( item ) )
				elif fail == 'PermissionDenied':
					msg  = "Server does allow to access a %s.Id (%s) while it should be disallowed!" % ( self.__response__, self.getId( item ))
				else:
					raise NotImplementedError

				self.assertPacketFail( packet, fail, msg )
			else:
				self.assertPacket( packet, self.__response__ )
				self.assertPacketEqual( packet, item )

class GetItemWithIDSlot( AuthorizedTestSession ):
	"""
	Must provide two class attributes:
	__request__  name of a request
	__response__ name of a expected response
	"""

	@property
	def item( self ):
		raise NotImplementedError

	@property
	def items( self ):
		return [ self.item ]

	def getId( self ):
		raise NotImplementedError

	def getSlot( self, item ):
		return item.id

	def __iter__( self ):
		Request = self.protocol.use( self.__request__ )

		items = list( self.items )

		response = yield Request( self.seq, self.getId(), [ self.getSlot( item ) for item in items ] )

		if isinstance( response, list ):
			packets = response[1:]
		else:
			packets = [ response ]

		for item, packet in zip( items, packets ):
			fail = self.getFail( item )

			if fail:
				if fail == 'NoSuchThing':
					msg  = "Server does return information for non-existent %s (id = %s, slot = %s)!" % ( self.__response__, self.getId(), self.getSlot( item ) )
				elif fail == 'PermissionDenied':
					msg  = "Server does allow to access a %s (id = %s, slot = %s) while it should be disallowed!" % ( self.__response__, self.getId(), self.getSlot( item ) )
				else:
					raise NotImplementedError

				self.assertPacketFail( packet, fail, msg )
			else:
				self.assertPacket( packet, self.__response__ )
				self.assertPacketEqual( packet, item )

class IDSequenceTestMixin( object ):
	@staticmethod
	def compareId( a, b ):
		return cmp( a.id, b.id )

	def assertIDSequenceEqual( self, idseq, items, remaining ):
		assert len( items ) > 0, "Sanity check for assertIDSequenceEqual failed!"

		obj_name = items[0].__origname__

		self.assertEqual( len( idseq.modtimes ), len( items ),
				"Expected to get %d %s objects, got %d instead." % ( len( items ), obj_name, len( idseq.modtimes ) ) )
		self.assertEqual( idseq.remaining, remaining,
				"Expected to be %d %s objects on the server, but %d left." % ( remaining, obj_name, idseq.remaining ) )

		objs = sorted( items, self.compareId )

		for item, obj in zip( sorted( idseq.modtimes, self.compareId ), objs ):
			obj_name  = obj.__origname__
			obj_mtime = self.datetimeToInt( obj.mtime )

			self.assertEqual( item.id, obj.id,
					"Expected id (%s) and %s.id (%s) to be equal" % ( item.id, obj_name, obj.id ) )
			self.assertEqual( item.modtime, obj_mtime, 
					"Expected modtime (%s) and %s.mtime (%s) to be equal." % ( item.modtime, obj_name, obj_mtime ) )

class GetItemIDs( AuthorizedTestSession, IDSequenceTestMixin ):
	def __iter__( self ):
		Request = self.protocol.use( self.__request__ )

		idseq = yield Request( self.seq, -1, 0, len( self.items ) )

		self.assertPacket( idseq, self.__response__ )
		self.assertIDSequenceEqual( idseq, self.items, 0 )

__all__ = [ 'ConnectedTestSession', 'AuthorizedTestSession',
			'GetWithIDWhenNotLogged', 'GetIDSequenceWhenNotLogged',
			'GetWithIDSlotWhenNotLogged', 'WhenNotLogged', 'GetItemWithID'
			'WithIDTestMixin', 'IDSequenceTestMixin', 'GetItemIDs',
			'GetItemWithIDSlot' ]
