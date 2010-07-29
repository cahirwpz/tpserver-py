#!/usr/bin/env python

from Common import FactoryMixin, RequestHandler, GetIDSequenceHandler, GetWithIDHandler

class ObjectFactoryMixin( FactoryMixin ):#{{{
	def toPacket( self, request, obj ):
		Object = self.protocol.use( 'Object' )

		return Object(
				request._sequence,
				obj.id,
				0,
				str( obj.name ),
				obj.size,
				[ obj.position.x, obj.position.y, obj.position.z ],
				[ obj.velocity.x, obj.velocity.y, obj.velocity.z ],
				[ child.id for child in obj.children ],
				[],
				0,
				self.datetimeToInt( obj.mtime ),
				"0" * 8,
				[] )
#}}}

class GetObjectIDs( GetIDSequenceHandler ):#{{{
	"""
	Request:  GetObjectIDs :: GetIDSequence
	Response: IDSequence
	"""
	__packet__ = 'ObjectIDs'
	__object__ = 'Object'
#}}}

class GetObjectIDsByContainer( RequestHandler ):#{{{
	"""
	Request:  GetObjectIDsByContainer
	Response: IDSequence
	"""

	# if not self.check( packet ):
	#	return True
	#
	# objects = Object.byparent(packet.id)
	#
	# return self.objects.Sequence(packet.sequence,)
#}}}

class GetObjectIDsByPos( RequestHandler ):#{{{
	"""
	Request:  GetObjectIDsByPos
	Response: IDSequence
	"""
#}}}

class GetObjectsByID( GetWithIDHandler, ObjectFactoryMixin ):#{{{
	"""
	Request:  GetObjectByID :: GetWithID
	Response: IDSequence
	"""
	# FIXME: This should show the correct number of orders for a certain person
	__packet__ = 'Object'
	__object__ = 'Object'
#}}}

class GetObjectsByPos( RequestHandler ):#{{{
	"""
	Request:  GetObjectsByPos
	Response: Object | Sequence + Object{2,n}
	"""
	def __init__( self ):
		objs = Object.bypos( request._pos, request._size )
		
		response = [ self.objects.Sequence( request._sequence, len( objs ) ) ]
		response.extend( [ obj.to_packet( self.player, request._sequence ) for obj in objs ] )

		return response
#}}}

__all__ = [ 'GetObjectIDs', 'GetObjectIDsByContainer', 'GetObjectIDsByPos',
			'GetObjectsByID', 'GetObjectsByPos' ]
