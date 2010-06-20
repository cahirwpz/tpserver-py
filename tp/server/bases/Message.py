#!/usr/bin/env python

from sqlalchemy import *

from tp.server.db import *
from tp.server.bases.SQL import SQLBase, SQLUtils, NoSuchThing

class MessageUtils( SQLUtils ):#{{{
	"""
	The realid class method starts here... 
	"""
	def realid(self, bid, slot):
		"""
		Message.realid(boardid, slot) -> id
		
		Returns the database id for the message found on board at slot.
		"""
		t = self.cls.table
		result = select([t.c.id], (t.c.bid==bid) & (t.c.slot==slot)).execute().fetchall()
		if len(result) != 1:
			return -1
		else:
			return result[0]['id']

	def number(self, bid):
		"""
		Message.number(boardid) -> number

		Returns the number of messages on an board.
		"""
		t = self.cls.table
		return select([func.count(t.c.id).label('count')], t.c.bid==bid).execute().fetchall()[0]['count']

	def findByIdAndSlot( self, _id, _slot ):
		result = DatabaseManager().session().query(Message).filter_by(bid=_id, slot=_slot).first()

		if result == None:
			raise NoSuchThing
		else:
			return result
#}}}

class Message( SQLBase ):#{{{
	"""
	Message with information about stuff.
	"""

	Utils = MessageUtils()

	@classmethod
	def getTable( cls, name, metadata, board_table ):
		table = Table( name, metadata,
					Column('id',      Integer,     primary_key = True),
					Column('board',   ForeignKey( "%s.id" % board_table ), nullable = False),
					Column('slot',	  Integer,     nullable = False),
					Column('subject', String(255), nullable = False),
					Column('body',    Binary,      nullable = False),
					Column('mtime',	  DateTime,    nullable = False,
						onupdate = func.current_timestamp(), default = func.current_timestamp()),
					UniqueConstraint('board', 'slot'))

		Index('idx_%s_board_slot', table.c.board, table.c.slot)
		
		return table

	@property
	def board(self):
		if not hasattr(self, "_board"):
			from Board import Board
			self._board = Board(self.bid)
		return self._board

	def insert(self):
		trans = dbconn.begin()
		try:
			t = self.table

			number = self.number(self.bid)
			if self.slot == -1:
				self.slot = number
			elif self.slot <= number:
				# Need to move all the other orders down
				update(t, (t.c.slot >= bindparam('s')) & (t.c.bid==bindparam('b')), {'slot': t.c.slot+1}).execute(s=self.slot, b=self.bid)
			else:
				raise NoSuchThing("Cannot insert to that slot number.")

			self.save()

			trans.commit()
		except Exception, e:
			trans.rollback()
			raise

	def save(self):
		trans = dbconn.begin()
		try:
			# Update the modtime...
			self.board.save()

			if not hasattr(self, 'id'):
				id = self.realid(self.bid, self.slot)
				if id != -1:
					self.id = id

			SQLBase.save(self)

			trans.commit()
		except Exception, e:
			trans.rollback()
			raise

	def remove(self):
		trans = dbconn.begin()
		try:
			# Move the other orders down
			t = self.table
			update(t, (t.c.slot >= bindparam('s')) & (t.c.bid==bindparam('b')), {'slot': t.c.slot-1}).execute(s=self.slot, b=self.bid)

			self.board.save()
			SQLBase.remove(self)

			trans.commit()
		except Exception, e:
			trans.rollback()
			raise

	def __str__(self):
		try:
			return "<Message id=%s bid=%s slot=%s>" % (self.id, self.bid, self.slot)
		except AttributeError:
			return "<Message id=(None) bid=%s slot=%s>" % (self.bid, self.slot)
#}}}

class Reference( SQLBase ):#{{{
	@classmethod
	def getTable( cls, name, metadata ):
		return Table( name, metadata,
				Column('id',          Integer,     index = True, primary_key = True),
				Column('value',       Integer,     nullable = False),
				Column('description', Binary,      nullable = False),
				Column('reference',   String(255), nullable = False))
#}}}

class MessageReference( SQLBase ):#{{{
	@classmethod
	def getTable( cls, name, metadata, message_table, reference_table ):
		table = Table( name, metadata,
				Column('id',        Integer,     index = True, primary_key = True),
				Column('message',   ForeignKey( "%s.id" % message_table )),
				Column('reference', ForeignKey( "%s.id" % reference_table )),
				Column('value',     Integer,  nullable=False, default = 0),
				Column('mtime',	    DateTime, nullable=False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()))

		Index('ix_%s_msg_ref' % name, table.c.message, table.c.reference)

		return table
#}}}

__all__ = [ 'Message', 'Reference', 'MessageReference' ]
