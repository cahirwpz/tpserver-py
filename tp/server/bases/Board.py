"""
Board which contains posts about stuff.
"""

from sqlalchemy import *

from tp.server.db import *
from tp.server.bases.SQL import SQLBase, SQLUtils

class BoardUtils( SQLUtils ):#{{{
	def realid(self, user, bid):
		# Board ID Zero gets map to player id
		if bid == 0:
			return user.id
		elif bid > 0:
			return bid
		else:
			raise NoSuchThing("No such board possible...")

	def mangleid(self, bid):
		if bid > 0:
			return 0
		else:
			return -bid

	def amount(self, user):
		"""
		amount(user)

		Get the number of records in this table (that the user can see).
		"""
		t = self.cls.table

		result = select([func.count(t.c.id).label('count')], (t.c.id<0) | (t.c.id==user.id)).execute().fetchall()

		if len(result) == 0:
			return 0
		else:
			return result[0]['count']

	def ids(self, user, start, amount):
		"""
		ids(user, start, amount)
		
		Get the last ids for this (that the user can see).
		"""
		t = self.cls.table

		if amount == -1:
			result = select([t.c.id, t.c.time], (t.c.id<0) | (t.c.id==user.id),
							order_by=[desc(t.c.time)], offset=start).execute().fetchall()
		else:
			result = select([t.c.id, t.c.time], (t.c.id<0) | (t.c.id==user.id),
							order_by=[desc(t.c.time)], limit=amount, offset=start).execute().fetchall()

		return [(self.cls.mangleid(x['id']), x['time']) for x in result] 
#}}}

class Board( SQLBase ):#{{{
	Utils = BoardUtils()

	table = Table('board', metadata,
				Column('game',	Integer,     nullable=False, index=True, primary_key=True),
				Column('id',	Integer,     nullable=False, index=True, primary_key=True),
				Column('name',	String(255), nullable=False, index=True),
				Column('desc',	Binary,      nullable=False),
				Column('time',	DateTime,    nullable=False, index=True,
					onupdate = func.current_timestamp(),
					default=func.current_timestamp()),
				ForeignKeyConstraint(['game'], ['game.id']))

	def __str__(self):
		return "<Board id=%s>" % self.id
#}}}
