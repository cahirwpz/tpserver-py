#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

class ReferenceParam( object ):
	@classmethod
	def InitMapper( cls, metadata, Parameter, ParameterType, Subject ):
		name = Subject.__origname__.lower()

		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',     ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('%s_id' % name, ForeignKey( Subject.id ), nullable = True ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = ParameterType, properties = {
			name : relation( Subject,
				uselist = False )
			})
	
class ObjectRefParam( ReferenceParam ):
	__maps_to__ = 'object'

class PlayerRefParam( ReferenceParam ):
	__maps_to__ = 'player'

class OrderTypeRefParam( ReferenceParam ):
	__maps_to__ = 'ordertype'

class OrderRefParam( ReferenceParam ):
	__maps_to__ = 'order'

class BoardRefParam( ReferenceParam ):
	__maps_to__ = 'board'

class MessageRefParam( ReferenceParam ):
	__maps_to__ = 'message'

class CategoryRefParam( ReferenceParam ):
	__maps_to__ = 'category'

class DesignRefParam( ReferenceParam ):
	__maps_to__ = 'design'

class ComponentRefParam( ReferenceParam ):
	__maps_to__ = 'component'

class PropertyRefParam( ReferenceParam ):
	__maps_to__ = 'property'

class ObjectTypeRefParam( ReferenceParam ):
	__maps_to__ = 'objecttype'

__all__ = [ 'ObjectRefParam', 'PlayerRefParam', 'OrderTypeRefParam',
			'OrderRefParam', 'BoardRefParam', 'MessageRefParam',
			'CategoryRefParam', 'DesignRefParam', 'ComponentRefParam',
			'PropertyRefParam', 'ObjectTypeRefParam' ]
