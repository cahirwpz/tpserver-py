#!/usr/bin/env python

from Common import GetWithIDHandler, GetIDSequenceHandler, FactoryMixin

class PropertyFactoryMixin( FactoryMixin ):#{{{
	def toPacket( self, request, obj ):
		Property = self.protocol.use( 'Property' )

		return Property(
				request._sequence,
				obj.id,
				self.datetimeToInt( obj.mtime ),
				sorted( cat.id for cat in obj.categories ),
				obj.rank,
				obj.name,
				obj.display_name,
				obj.description,
				obj.calculate,
				obj.requirements )
#}}}

class GetProperty( GetWithIDHandler, PropertyFactoryMixin ):#{{{
	"""
	Request:  GetProperty :: GetWithID
	Response: Property | Sequence + Property{2,n}
	"""
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
