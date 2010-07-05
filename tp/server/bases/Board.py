#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref 

from tp.server.db import DatabaseManager

from SQL import SQLBase, NoSuchThing

class Board( SQLBase ):#{{{
	"""
	Board which contains posts about stuff.
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

	@classmethod
	def ByRealId( cls, user, id ):
		if id == 0:
			return cls.ById( user.id )
		else:
			return cls.ById( id )
	
	#{{{
	# def realid(self, user, bid):
	#	# Board ID Zero gets map to player id
	#	if bid == 0:
	#		return user.id
	#	elif bid > 0:
	#		return bid
	#	else:
	#		raise NoSuchThing("No such board possible...")

	# def mangleid(self, bid):
	#	if bid > 0:
	#		return 0
	#	else:
	#		return -bid

	# def amount(self, user):
	#	"""
	#	amount(user)
	#
	#	Get the number of records in this table (that the user can see).
	#	"""
	#	t = self.cls.table
	#
	#	result = select([func.count(t.c.id).label('count')], (t.c.id<0) | (t.c.id==user.id)).execute().fetchall()
	#
	#	if len(result) == 0:
	#		return 0
	#	else:
	#		return result[0]['count']

	# def ids(self, user, start, amount):
	#	"""
	#	ids(user, start, amount)
	#	
	#	Get the last ids for this (that the user can see).
	#	"""
	#	t = self.cls.table
	#
	#	if amount == -1:
	#		result = select([t.c.id, t.c.time], (t.c.id<0) | (t.c.id==user.id),
	#						order_by=[desc(t.c.time)], offset=start).execute().fetchall()
	#	else:
	#		result = select([t.c.id, t.c.time], (t.c.id<0) | (t.c.id==user.id),
	#						order_by=[desc(t.c.time)], limit=amount, offset=start).execute().fetchall()
	#
	#	return [(self.cls.mangleid(x['id']), x['time']) for x in result]
	#}}}

	def __str__(self):
		return "<%s id=%s>" % ( self.__class__.__name__, self.id )
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

		Index('idx_%s_board_msg' % cls.__tablename__, cols.board_id, cols.message_id)
		Index('idx_%s_board_slot' % cls.__tablename__, cols.board_id, cols.number)

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
