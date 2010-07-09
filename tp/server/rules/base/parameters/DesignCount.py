#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

from GenericListParam import *

from tp.server.bases import SQLBase, GenericList

class DesignCount( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Design ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',        ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('design_id', ForeignKey( Design.id ), nullable = False ),
				Column('count',     Integer ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'DesignCount', properties = {
			'design': relation( Design,
				uselist = False )
			})
#}}}

class DesignCountList( GenericList ):#{{{
	pass
#}}}

class DesignCountListParam( GenericListParam ):#{{{
	pass
#}}}

__all__ = [ 'DesignCount', 'DesignCountList', 'DesignCountListParam' ]
