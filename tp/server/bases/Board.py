
from config import db, netlib

from SQL import *
from Message import Message

class Board(SQLBase):
	tablename = "`board`"

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
		result = db.query("SELECT count(*) FROM %(tablename)s WHERE id < 0 OR id = %(userid)s", tablename=cls.tablename, userid=user.id)
		if len(result) == 0:
			return 0
		return result[0]['count(*)']
	amount = classmethod(amount)

	def ids(cls, user, start, amount):
		"""\
		ids(user, start, amount)
		
		Get the last ids for this (that the user can see).
		"""
		if amount == -1:
			amount = 2**64
		
		result = db.query("SELECT id, time FROM %(tablename)s WHERE id < 0 OR id = %(userid)s ORDER BY time DESC LIMIT %(amount)s OFFSET %(start)s", tablename=cls.tablename, userid=user.id, start=start, amount=amount)
		return [(cls.mangleid(x['id']), x['time']) for x in result] 
	ids = classmethod(ids)

	def to_packet(self, sequence):
		return netlib.objects.Board(sequence, Board.mangleid(self.id), self.name, self.desc, Message.number(self.id), self.time)

	def id_packet(cls):
		return netlib.objects.Board_IDSequence
	id_packet = classmethod(id_packet)

	def __str__(self):
		return "<Board id=%s>" % (self.id)



