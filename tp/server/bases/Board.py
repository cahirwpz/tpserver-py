
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
		elif bid > 0:
			return bid * -1
		else:
			raise NoSuch("No such board possible...")
	realid = staticmethod(realid)

	def mangleid(bid):
		if bid > 0:
			return 0
		else:
			return bid * -1
	mangleid = staticmethod(mangleid)

	def all():
		results = db.query("""SELECT id FROM %(tablename)s WHERE id < 0""", tablename=Board.tablename)
		return [0,]+[-1*x['id'] for x in results]
	all = staticmethod(all)

	def next(id):
		if results == -1:
			return 0
		else:
			result = db.query("""SELECT id FROM %(tablename)s WHERE id > %(id)s LIMIT 1""", tablename=Message.tablename, id=id)
			if len(results) > 0:
				return result[0]['id']
			else:
				raise NoSuch("No board after given...")
	next = staticmethod(next)

	def to_packet(self, sequence):
		return netlib.objects.Board(sequence, Board.mangleid(self.id), self.name, self.desc, Message.number(self.id))

	def __str__(self):
		return "<Board id=%s>" % (self.id)

