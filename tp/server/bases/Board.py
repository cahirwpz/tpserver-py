
import db
import netlib

from SQL import *
from Message import Message

class Board(SQLBase):
	tablename = "tp.board"

	def realid(bid, pid):
		# Board ID Zero gets map to player id
		# Board ID != Zero gets mapped to negative
		if bid == 0:
			return pid
		else:
			return bid * -1
	realid = staticmethod(realid)

	def to_packet(self, sequence):
		return netlib.objects.Board(sequence, self.id, self.name, self.desc, Message.number(self.id))

	def __str__(self):
		return "<Board id=%s>" % (self.id)

