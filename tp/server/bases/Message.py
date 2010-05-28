"""
Message with information about stuff (and references to other objects).
"""

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
	Utils = MessageUtils()

	table = Table('message', metadata,
				Column('game', 	  Integer,     nullable=False, index=True), #, primary_key=True),
				Column('id',	  Integer,     primary_key=True),
				Column('bid',	  Integer,     nullable=False, index=True),
				Column('slot',	  Integer,     nullable=False),
				Column('subject', String(255), nullable=False, index=True),
				Column('body',    Binary,      nullable=False),
				Column('time',	  DateTime,    nullable=False, index=True,
					onupdate=func.current_timestamp(),
					default=func.current_timestamp()),
				UniqueConstraint('game', 'bid', 'slot'),
				ForeignKeyConstraint(['bid'],  ['board.id']),
				ForeignKeyConstraint(['game'], ['game.id']))

	Index('idx_message_bidslot', table.c.bid, table.c.slot)

	table_types = Table('reference', metadata,
		Column('game', 	Integer,     nullable=False, index=True, primary_key=True),
		Column('id',    Integer,     nullable=False, primary_key=True),
		Column('value', Integer,     nullable=False, index=True),
		Column('desc',  Binary,      nullable=False),
		Column('ref',   String(255), nullable=False))

	table_references = Table('message_references', metadata,
				Column('game', 	Integer,  nullable=False, primary_key=True),
				Column('mid',   Integer,  nullable=False, primary_key=True),
				Column('rid',   Integer,  nullable=False, primary_key=True),
				Column('value', Integer,  nullable=False, default=0),
				Column('time',	DateTime, nullable=False, index=True,
					onupdate = func.current_timestamp(),
					default=func.current_timestamp()),
				ForeignKeyConstraint(['mid'],  ['message.id']),
				ForeignKeyConstraint(['rid'],  ['reference.id']),
				ForeignKeyConstraint(['game'], ['game.id']))

	Index('idx_msgref_midrid', table_references.c.mid, table_references.c.rid)

	def allowed(self, user):
		# FIXME: This is a hack.
		return self.board.allowed(user)

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

from sqlalchemy.orm import mapper

mapper(Message, Message.table)
