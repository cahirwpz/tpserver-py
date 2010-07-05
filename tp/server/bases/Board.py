#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref 

from tp.server.db import DatabaseManager

from SQL import SQLBase, NoSuchThing

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

class Slot( SQLBase ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Board, Message ):
		cls.__table__ = Table( cls.__tablename__, metadata,
					Column('board_id',   ForeignKey( Board.id ), index = True, primary_key = True),
					Column('message_id', ForeignKey( Message.id ), index = True, primary_key = True),
					Column('number',	 Integer, index = True, nullable = False),
					Column('mtime',	     DateTime, nullable = False,
						onupdate = func.current_timestamp(), default = func.current_timestamp()),
					UniqueConstraint('board_id', 'number'))

		cols = cls.__table__.c

		Index('ix_%s_board_msg' % cls.__tablename__, cols.board_id, cols.message_id)
		Index('ix_%s_board_slot' % cls.__tablename__, cols.board_id, cols.number)

		mapper( cls, cls.__table__, properties = {
			'board': relation( Board,
				uselist = False,
				single_parent = True,
				backref = backref( 'slots' ),
				cascade = 'all, delete, delete-orphan'),
			'message': relation( Message,
				uselist = False,
				single_parent = True,
				backref = backref( 'slot', uselist = False ),
				cascade = 'all, delete, delete-orphan')
			})
	
	@classmethod
	def ByIdAndNumber( cls, id, number ):
		obj = DatabaseManager().query( cls ).filter( and_( cls.board_id == id, cls.number == number ) ).first()

		if not obj:
			raise NoSuchThing

		return obj

	@property
	def content( self ):
		return self.message
#}}}

__all__ = [ 'Board', 'Slot' ]
