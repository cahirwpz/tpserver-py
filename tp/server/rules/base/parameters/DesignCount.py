#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

class DesignCountParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, Design ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('design_id', ForeignKey( Design.id ), nullable = False ),
				Column('count',     Integer ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'DesignCount', properties = {
			'design': relation( Design,
				uselist = False )
			})
#}}}

__all__ = [ 'DesignCountParam' ]
