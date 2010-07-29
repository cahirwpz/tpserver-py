#!/usr/bin/env python

from Common import FactoryMixin, GetWithIDHandler, GetIDSequenceHandler

class ComponentFactoryMixin( FactoryMixin ):#{{{
	def toPacket( self, request, component ):
		Component = self.protocol.use( 'Component' )

		return Component(
				request._sequence,
				component.id,
				self.datetimeToInt( component.mtime ),
				component.categories,
				component.name,
				component.description,
				component.requirements,
				component.properties )
#}}}

class GetComponent( GetWithIDHandler, ComponentFactoryMixin ):#{{{
	"""
	Request:  GetComponent :: GetWithID
	Response: Component | Sequence + Component{2,n}
	"""
	__object__ = 'Component'
#}}}

class GetComponentIDs( GetIDSequenceHandler ):#{{{
	"""
	Request:  GetComponentIDs :: GetIDSequence
	Response: IDSequence
	"""
	__packet__ = 'ComponentIDs'
	__object__ = 'Component'
#}}}

__all__ = [ 'GetComponent', 'GetComponentIDs' ]
