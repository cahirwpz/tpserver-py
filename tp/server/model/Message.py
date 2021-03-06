#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref
from sqlalchemy.ext.orderinglist import ordering_list

from Model import ModelObject

class MessageReference( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata, Message, Reference ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('message_id',   ForeignKey( Message.id ), index = True, primary_key = True),
				Column('reference_id', ForeignKey( Reference.id ), index = True, primary_key = True),
				Column('value',        Integer,  nullable = False, default = 0),
				Column('mtime',	       DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		cols = cls.__table__.c

		Index('ix_%s_msg_ref' % cls.__tablename__, cols.message_id, cols.reference_id)

		mapper( cls, cls.__table__, properties = {
			'reference': relation( Reference, backref = 'message' )
			})

class Message( ModelObject ):
	"""
	Message with information about stuff.
	"""

	@classmethod
	def InitMapper( cls, metadata, Board ):
		cls.__table__ = Table( cls.__tablename__, metadata,
					Column('id',        Integer, index = True, primary_key = True ),
					Column('board_id',  ForeignKey( Board.id ), index = True, nullable = False ),
					Column('slot',      Integer, index = True, nullable = False ),
					Column('subject',   String(255), nullable = False ),
					Column('body',      Text, nullable = False ),
					Column('turn',		Integer, nullable = False ),
					Column('mtime',	    DateTime, nullable = False,
						onupdate = func.current_timestamp(), default = func.current_timestamp()))

		cols = cls.__table__.c

		Index('ix_%s_id_board' % cls.__tablename__, cols.id, cols.board_id)

		mapper( cls, cls.__table__, properties = {
			'board': relation( Board,
				uselist = False,
				backref = backref( 'messages',
					collection_class = ordering_list('slot', count_from = 1),
					order_by = [ cols.slot ] ))
			})
	
	def __str__( self ):
		return '<%s@%s id="%s" board="%s" slot="%s" subject="%s">' % \
				( self.__origname__, self.__game__.name, self.id, self.board.id, self.slot, self.subject )

__all__ = [ 'Message', 'MessageReference' ]
