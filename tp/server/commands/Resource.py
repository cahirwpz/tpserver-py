#!/usr/bin/env python

from Common import GetWithIDHandler, GetIDSequenceHandler, FactoryMixin

class ResourceFactoryMixin( FactoryMixin ):#{{{
	def toPacket( self, request, obj ):
		Resource = self.protocol.use( 'Resource' )

		return Resource(
				request._sequence,
				obj.id,
				obj.name_singular,
				obj.name_plural,
				obj.unit_singular,
				obj.unit_plural,
				obj.description,
				obj.weight,
				obj.size,
				self.datetimeToInt( obj.mtime ) )
#}}}

class GetResource( GetWithIDHandler, ResourceFactoryMixin ):#{{{
	"""
	Request:  GetResource :: GetWithID
	Response: Resource | Sequence + Resource{2,n}
	"""
	__object__ = 'ResourceType'
#}}}

class GetResourceIDs( GetIDSequenceHandler ):#{{{
	"""
	Request:  GetResourceIDs :: GetIDSequence
	Response: IDSequence
	"""
	__packet__ = 'ResourceIDs'
	__object__ = 'ResourceType'
#}}}

__all__ = [ 'GetResource', 'GetResourceIDs' ]
