"""\
Message with information about stuff (and references to other objects).
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.db import *
from tp import netlib
from SQL import SQLBase

table_types = Table('reference',
	Column('game', 	Integer,     nullable=False, index=True, primary_key=True),
	Column('id',    Integer,     nullable=False, primary_key=True),
	Column('value', Integer,     nullable=False, index=True),
	Column('desc',  Binary,      nullable=False),
	Column('ref',   String(255), nullable=False),
)

class Message(SQLBase):
	table = Table('message',
		Column('game', 	  Integer,     nullable=False, index=True, primary_key=True),
		Column('id',	  Integer,     nullable=False, index=True, primary_key=True),
		Column('bid',	  Integer,     nullable=False, index=True),
		Column('slot',	  Integer,     nullable=False),
		Column('subject', String(255), nullable=False, index=True),
		Column('body',    Binary,      nullable=False),
		Column('time',	  DateTime,    nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		UniqueConstraint('bid', 'slot'),
		ForeignKeyConstraint(['bid'],  ['board.id']),
		ForeignKeyConstraint(['game'], ['game.id']),
	)
	Index('idx_message_bidslot', table.c.bid, table.c.slot),

	table_references = Table('message_references',
		Column('game', 	Integer,  nullable=False, primary_key=True),
		Column('mid',   Integer,  nullable=False, primary_key=True),
		Column('rid',   Integer,  nullable=False, primary_key=True),
		Column('value', Integer,  nullable=False, default=0),
		Column('time',	DateTime, nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		ForeignKeyConstraint(['mid'],  ['message.id']),
		ForeignKeyConstraint(['rid'],  ['reference.id']),
		ForeignKeyConstraint(['game'], ['game.id']),
	)
	Index('idx_msgref_midrid', table_references.c.mid, table_references.c.rid),

	def realid(cls, bid, slot):
		t = cls.table
		result = select([t.c.id], (t.c.bid==bid) & (t.c.slot==slot)).execute().fetchall()
		if len(result) != 1:
			return -1
		else:
			return result[0]['id']
	realid = classmethod(realid)

	def number(cls, bid):
		t = cls.table
		return select([func.count(t.c.id).label('count')], t.c.bid==bid).execute().fetchall()[0]['count']
	number = classmethod(number)

	def __init__(self, id=None, slot=None):
		SQLBase.__init__(self)

		if id != None and slot != None:
			self.load(id, slot)

	def load(self, bid, slot):
		id = self.realid(bid, slot)
		if id == -1:
			raise NoSuch("Order %s %s does not exists" % (bid, slot))
			
		SQLBase.load(self, id)

	def insert(self):
		number = self.number(self.bid)
		if self.slot == -1:
			self.slot = number
		elif self.slot <= number:
			# Need to move all the other orders down
			t = self.table
			update(t, (t.c.slot>=self.slot) & (t.c.bid==self.bid)).execute(slot=t.c.slot+1)
		else:
			raise NoSuch("Cannot insert to that slot number.")
		
		self.save()

	def save(self):
		if not hasattr(self, 'id'):
			id = self.realid(self.bid, self.slot)
			if id != -1:
				self.id = id
			
		SQLBase.save(self)

	def remove(self):
		# Move the other orders down
		t = self.table
		update(t, (t.c.slot>=self.slot) & (t.c.bid==self.bid)).execute(slot=t.c.slot-1)

		SQLBase.remove(self)

	def to_packet(self, sequence):
		# FIXME: The reference system needs to be added and so does the turn
		return netlib.objects.Message(sequence, self.bid, self.slot, [], self.subject, self.body, 0, [])

	def from_packet(self, user, packet):
		self = SQLBase.from_packet(cls, user, packet)

		# The ID from the packet is the Board ID.
		self.bid = self.id
		del self.id

	from_packet = classmethod(from_packet)

	def __str__(self):
		return "<Message id=%s bid=%s slot=%s>" % (self.id, self.bid, self.slot)

