"""
Board which contains posts about stuff.
"""

from sqlalchemy import *

from tp.server.db import *
from tp.server.bases.SQL import SQLBase

class Board( SQLBase ):#{{{
	table = Table('board', metadata,
				Column('game',	Integer,     nullable=False, index=True, primary_key=True),
				Column('id',	Integer,     nullable=False, index=True, primary_key=True),
				Column('name',	String(255), nullable=False, index=True),
				Column('desc',	Binary,      nullable=False),
				Column('time',	DateTime,    nullable=False, index=True,
					onupdate = func.current_timestamp(),
					default=func.current_timestamp()),
				ForeignKeyConstraint(['game'], ['game.id']))

	@classmethod
	def realid(cls, user, bid):
		# Board ID Zero gets map to player id
		# Board ID != Zero gets mapped to negative
		if bid == 0:
			return user.id
		elif bid > 0:
			return bid * -1
		else:
			raise NoSuch("No such board possible...")

	@classmethod
	def mangleid(cls, bid):
		if bid > 0:
			return 0
		else:
			return -bid

	@classmethod
	def amount(cls, user):
		"""
		amount(user)

		Get the number of records in this table (that the user can see).
		"""
		t = cls.table
		result = select([func.count(t.c.id).label('count')], (t.c.id<0) | (t.c.id==user.id)).execute().fetchall()
		if len(result) == 0:
			return 0
		return result[0]['count']

	@classmethod
	def ids(cls, user, start, amount):
		"""
		ids(user, start, amount)
		
		Get the last ids for this (that the user can see).
		"""
		t = cls.table
		if amount == -1:
			result = select([t.c.id, t.c.time], (t.c.id<0) | (t.c.id==user.id),
							order_by=[desc(t.c.time)], offset=start).execute().fetchall()
		else:
			result = select([t.c.id, t.c.time], (t.c.id<0) | (t.c.id==user.id),
							order_by=[desc(t.c.time)], limit=amount, offset=start).execute().fetchall()
		return [(cls.mangleid(x['id']), x['time']) for x in result] 

	def __str__(self):
		return "<Board id=%s>" % (self.id)
#}}}
