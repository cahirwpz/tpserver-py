#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

from SQL import SQLBase

class MessageReference( SQLBase ):#{{{
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
#}}}

class Message( SQLBase ):#{{{
	"""
	Message with information about stuff.
	"""

	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
					Column('id',        Integer, primary_key = True),
					Column('subject',   String(255), nullable = False),
					Column('body',      Text, nullable = False),
					Column('mtime',	    DateTime, nullable = False,
						onupdate = func.current_timestamp(), default = func.current_timestamp()))

		mapper( cls, cls.__table__ )

	def __str__(self):
		return '<%s@%s id="%d">' % ( self.__origname__, self.__game__.__name__, self.id )
#}}}

__all__ = [ 'Message', 'MessageReference' ]
