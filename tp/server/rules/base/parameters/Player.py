#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

class PlayerParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, Player ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('player_id', ForeignKey( Player.id ), index = True, nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'Player',
				properties = {
					'player' : relation( Player,
						uselist = False )
					})
#}}}

__all__ = [ 'PlayerParam' ]
