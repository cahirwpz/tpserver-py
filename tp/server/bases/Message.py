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

		cols = cls.__table__.c

		mapper( cls, cls.__table__ )
		#, properties = {
		#	'reference' : relation( MessageReference, backref = "message" ),
		#	'slot':       relation( Slot, uselist = False, backref = "message" )
		#	})

# {{{
	# def realid(self, bid, slot):
	#	"""
	#	Message.realid(boardid, slot) -> id
	#	
	#	Returns the database id for the message found on board at slot.
	#	"""
	#	t = self.cls.table
	#	result = select([t.c.id], (t.c.bid==bid) & (t.c.slot==slot)).execute().fetchall()
	#	if len(result) != 1:
	#		return -1
	#	else:
	#		return result[0]['id']

	# def number(self, bid):
	#	"""
	#	Message.number(boardid) -> number
	#
	#	Returns the number of messages on an board.
	#	"""
	#	t = self.cls.table
	#	return select([func.count(t.c.id).label('count')], t.c.bid==bid).execute().fetchall()[0]['count']

	# def findByIdAndSlot( self, _id, _slot ):
	#	result = None
	#
	#	with DatabaseManager().session() as session:
	#		result = session.query( self.cls ).filter_by( board = _id, slot = _slot).first()
	#
	#	if result is None:
	#		raise NoSuchThing
	#
	#	return result
#}}}

	def __str__(self):
		try:
			return "<Message id=%s>" % self.id
		except AttributeError:
			return "<Message>"
#}}}

__all__ = [ 'Message', 'MessageReference' ]
