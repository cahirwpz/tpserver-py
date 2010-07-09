#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

class GenericListParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, List ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('list_id',   ForeignKey( List.id ), nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = List.__origname__, properties = {
			'list': relation( List, 
				uselist = False )
			})
#}}}

__all__ = [ 'GenericListParam' ]
