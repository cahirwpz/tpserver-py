#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

from SQL import SQLBase, SelectableByName

class Category( SQLBase, SelectableByName ):#{{{
	"""
	Categories which help group things together.
	"""

	@classmethod
	def InitMapper( cls, metadata, Player ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',          Integer, index = True, primary_key = True),
				Column('owner_id',    ForeignKey( Player.id ), index = True, nullable = True ),
				Column('name',        String(255), index = True, nullable = False),
				Column('description', Text, nullable = False),
				Column('mtime',       DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()),
				UniqueConstraint( 'owner_id', 'name' ) )

		mapper( cls, cls.__table__, properties = {
			'owner': relation( Player,
				uselist = False )
			})

	def __str__( self ):
		return '<%s@%s id="%s" name="%s" owner="%s">' % ( self.__origname__, self.__game__.name, self.id, self.name, self.owner_id )
#}}}

__all__ = [ 'Category' ]
