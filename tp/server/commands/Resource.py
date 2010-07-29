#!/usr/bin/env python

from Common import GetWithIDHandler, GetIDSequenceHandler

class ResourceFactoryMixin( object ):#{{{
	def toPacket( self, request, obj ):
		Resource = self.protocol.use( 'Resource' )

		return Resource(
				request._sequence,
				obj.id,
				obj.namesingular,
				obj.nameplural,
				obj.unitsingular,
				obj.unitplural,
				obj.desc,
				obj.weight,
				obj.size,
				obj.time )
#}}}

class GetResource( GetWithIDHandler, ResourceFactoryMixin ):#{{{
	"""
	Request:  GetResource :: GetWithID
	Response: Resource | Sequence + Resource{2,n}
	"""
	__object__ = 'Resource'
#}}}

class GetResourceIDs( GetIDSequenceHandler ):#{{{
	"""
	Request:  GetResourceIDs :: GetIDSequence
	Response: IDSequence
	"""
	__packet__ = 'ResourceIDs'
	__object__ = 'Resource'
#}}}

__all__ = [ 'GetResource', 'GetResourceIDs' ]
