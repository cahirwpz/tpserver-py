
from config import db, netlib

from SQL import *
from Message import Message

class Board(SQLBase):
	tablename = "`board`"

	def realid(bid, pid):
		# Board ID Zero gets map to player id
		# Board ID != Zero gets mapped to negative
		if bid == 0:
			return pid
		else:
			return bid * -1
	realid = staticmethod(realid)

	def mangleid(bid):
		if bid > 0:
			return 0
		else:
			return bid * -1
	mangleid = staticmethod(mangleid)

	def to_packet(self, sequence):
		return netlib.objects.Board(sequence, Board.mangleid(self.id), self.name, self.desc, Message.number(self.id))

	def __str__(self):
		return "<Board id=%s>" % (self.id)

