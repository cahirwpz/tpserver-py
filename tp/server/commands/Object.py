#!/usr/bin/env python

from Common import FactoryMixin, RequestHandler, GetIDSequenceHandler, GetWithIDHandler, MustBeLogged
from tp.server.model import Vector3D

class ObjectFactoryMixin( FactoryMixin ):
	def toPacket( self, request, obj ):
		Object = self.protocol.use( 'Object' )

		try:
			velocity = obj.velocity.vector
		except AttributeError:
			velocity = None

		if not velocity:
			velocity = Vector3D(0,0,0)

		return Object(
				request._sequence,
				obj.id,
				obj.type.id,
				str( obj.name ),
				obj.size,
				[ obj.position.x, obj.position.y, obj.position.z ],
				[ velocity.x, velocity.y, velocity.z ],
				[ child.id for child in obj.children ],
				[ order_object.order_type_id for order_object in obj.type.order_types ],
				len( obj.orders ),
				self.datetimeToInt( obj.mtime ),
				"0" * 8,
				[] )

class GetObjectIDs( GetIDSequenceHandler ):
	"""
	Request:  GetObjectIDs :: GetIDSequence
	Response: IDSequence
	"""
	__packet__ = 'ObjectIDs'
	__object__ = 'Object'

class GetObjectIDsByContainer( RequestHandler ):
	"""
	Request:  GetObjectIDsByContainer
	Response: IDSequence
	"""
	@MustBeLogged
	def __call__( self, request ):
		Object = self.model.use( 'Object' )

		parent = Object.ByID( request.id )

		response = [ obj.id for obj in Object.query().filter( Object.parent_id == parent.id ).all() ]

		if len( response ) > 1:
			response.insert( 0, self.Sequence( request, len( response ) ) )
		
		return response

class GetObjectIDsByPos( RequestHandler ):
	"""
	Request:  GetObjectIDsByPos
	Response: IDSequence
	"""
	@MustBeLogged
	def __call__( self, request ):
		pass

class GetObjectsByID( GetWithIDHandler, ObjectFactoryMixin ):
	"""
	Request:  GetObjectByID :: GetWithID
	Response: IDSequence
	"""
	# FIXME: This should show the correct number of orders for a certain person
	__object__ = 'Object'

class GetObjectsByPos( RequestHandler ):
	"""
	Request:  GetObjectsByPos
	Response: Object | Sequence + Object{2,n}
	"""
	@MustBeLogged
	def __call__( self, request ):
		Object = self.model.use( 'Object' )

		objs = Object.ByPos( request.pos, request.size )
		
		response = [ self.objects.Sequence( request._sequence, len( objs ) ) ]
		response.extend( [ obj.to_packet( self.player, request._sequence ) for obj in objs ] )

		return response

__all__ = [ 'GetObjectIDs', 'GetObjectIDsByContainer', 'GetObjectIDsByPos',
			'GetObjectsByID', 'GetObjectsByPos' ]
