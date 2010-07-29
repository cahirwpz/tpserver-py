#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref 

from SQL import SQLBase

class Board( SQLBase ):#{{{
	"""
	Board which contains posts about stuff.

	Notes: Board ID Zero gets map to player id
	"""
	@classmethod
	def InitMapper( cls, metadata, Player ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',          Integer, index = True, primary_key = True ),
				Column('owner_id',    ForeignKey( Player.id ), index = True, nullable = True ),
				Column('name',        String(255), nullable = False ),
				Column('description', Text, nullable = False ),
				Column('mtime',	      DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		mapper( cls, cls.__table__, properties = {
			'owner': relation( Player,
				uselist = False,
				backref = backref( 'board', uselist = False ),
				cascade = 'all')
			})

	def __str__(self):
		return '<%s@%s id="%d" name="%s">' % ( self.__origname__, self.__game__.__name__, self.id, self.name )
#}}}

__all__ = [ 'Board' ]
