#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

class GenericReferenceParam( object ):
	# TODO: constraint checking!
	# - 'reference' must be present in 'allowed' list
	# - 'allowed' list items must be unique
	@classmethod
	def InitMapper( cls, metadata, Parameter, ParameterType, NumberList ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',        ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('reference',       Integer, nullable = False ),
				Column('allowed_list_id', ForeignKey( NumberList.id ), nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = ParameterType, properties = {
			'allowed' : relation( NumberList,
				primaryjoin = cls.__table__.c.allowed_list_id == NumberList.__table__.c.id,
				collection_class = set )
			})

__all__ = [ 'GenericReferenceParam' ]
