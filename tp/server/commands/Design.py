#!/usr/bin/env python

from Common import ( FactoryMixin, MustBeLogged, RequestHandler,
		GetWithIDHandler, GetIDSequenceHandler, RemoveWithIDHandler )

class DesignFactoryMixin( FactoryMixin ):#{{{
	def toPacket( self, request, obj ):
		Design = self.protocol.use( 'Design' )

		return Design( request._sequence,
				obj.id,
				self.datetimeToInt( obj.mtime ),
				[ category.id for category in obj.categories ],
				obj.name,
				obj.description,
				0, # TODO: usage 
				obj.owner if obj.owner else -1,
				[ ( component.component_id, component.amount ) for component in obj.components ],
				obj.comment,
				[ [ prop.property_id, prop.value ] for prop in obj.properties ] )
#}}}

class AddDesign( RequestHandler ):#{{{
	"""
	Request:  AddDesign :: Design
	Response: Design | Fail
	"""

	@MustBeLogged
	def __call__( self, request ):
		pass
#}}}

class GetDesign( GetWithIDHandler, DesignFactoryMixin ):#{{{
	"""
	Request:  GetDesign :: GetWithID
	Response: Design | Sequence + Design{2,n}
	"""
	__object__ = 'Design'
#}}}

class GetDesignIDs( GetIDSequenceHandler ):#{{{
	"""
	Request:  GetDesignIDs :: GetIDSequence
	Response: IDSequence
	"""
	__packet__ = 'DesignIDs'
	__object__ = 'Design'
#}}}

class ModifyDesign( RequestHandler ):#{{{
	"""
	Request:  ModifyDesign :: Design
	Response: Design | Fail
	"""

	@MustBeLogged
	def __call__( self, request ):
		pass
#}}}

class RemoveDesign( RemoveWithIDHandler ):#{{{
	"""
	Request:  RemoveDesign :: GetDesign :: GetWithID
	Response: ( Okay | Fail ) | Sequence + ( Okay | Fail ){2,n}
	"""
	def authorize( self, design ):
		return bool( design.owner == self.player )
#}}}

__all__ = [ 'AddDesign', 'GetDesign', 'GetDesignIDs', 'ModifyDesign', 'RemoveDesign' ]
