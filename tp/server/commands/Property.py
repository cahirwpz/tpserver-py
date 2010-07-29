#!/usr/bin/env python

from Common import GetWithIDHandler, GetIDSequenceHandler

class PropertyFactoryMixin( object ):#{{{
	def toPacket( self, request, obj ):
		Property = self.protocol.use( 'Property' )

		return Property(
				request._sequence,
				obj.id,
				obj.time,
				obj.categories,
				obj.rank,
				obj.name,
				obj.displayname,
				obj.desc,
				obj.calculate,
				obj.requirements )
#}}}

class GetProperty( GetWithIDHandler, PropertyFactoryMixin ):#{{{
	"""
	Request:  GetProperty :: GetWithID
	Response: Property | Sequence + Property{2,n}
	"""
	__packet__ = 'Property'
	__object__ = 'Property'
#}}}

class GetPropertyIDs( GetIDSequenceHandler ):#{{{
	"""
	Request:  GetPropertyIDs :: GetIDSequence
	Response: IDSequence
	"""
	__packet__ = 'PropertyIDs'
	__object__ = 'Property'
#}}}

__all__ = [ 'GetProperty', 'GetPropertyIDs' ]
