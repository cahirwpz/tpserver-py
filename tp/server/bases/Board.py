"""\
Board which contains posts about stuff.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.db import *
from tp import netlib
from SQL import SQLBase
from Message import Message

class Board(SQLBase):
	table = Table('board',
		Column('game',	Integer,     nullable = False, index=True),
		Column('id',	Integer,     nullable = False, index=True, primary_key=True),
		Column('name',	String(255), nullable = False, index=True),
		Column('desc',	Binary,      nullable = False),
		Column('time',	DateTime,    nullable = False, index=True, onupdate=func.current_timestamp()),

		ForeignKeyConstraint(['game'], ['game.id']),
	)

	def realid(cls, user, bid):
		# Board ID Zero gets map to player id
		# Board ID != Zero gets mapped to negative
		if bid == 0:
			return user.id
		elif bid > 0:
			return bid * -1
		else:
			raise NoSuch("No such board possible...")
	realid = classmethod(realid)

	def mangleid(cls, bid):
		if bid > 0:
			return 0
		else:
			return bid * -1
	mangleid = classmethod(mangleid)

	def amount(cls, user):
		"""\
		amount(user)

		Get the number of records in this table (that the user can see).
		"""
		t = cls.table
		result = select([func.count(t.c.id).label('count')], (t.c.id<0) | (t.c.id==user.id)).execute().fetchall()
		if len(result) == 0:
			return 0
		return result[0]['count']
	amount = classmethod(amount)

	def ids(cls, user, start, amount):
		"""\
		ids(user, start, amount)
		
		Get the last ids for this (that the user can see).
		"""
		if amount == -1:
			amount = 2**64
		
		t = cls.table
		result = select([t.c.id, t.c.time], (t.c.id<0) | (t.c.id==user.id),
							order_by=[desc(t.c.time)], limit=amount, offset=start).execute().fetchall()
		return [(cls.mangleid(x['id']), x['time']) for x in result] 
	ids = classmethod(ids)

	def to_packet(self, sequence):
		b = Board.mangleid(self.id)
		m = Message.number(self.id)
		print "--------------------------- Board", b, "Message", m
		print repr([sequence, Board.mangleid(self.id), self.name, self.desc, Message.number(self.id), self.time])
		return netlib.objects.Board(sequence, Board.mangleid(self.id), self.name, self.desc, Message.number(self.id), self.time)

	def id_packet(cls):
		return netlib.objects.Board_IDSequence
	id_packet = classmethod(id_packet)

	def __str__(self):
		return "<Board id=%s>" % (self.id)



