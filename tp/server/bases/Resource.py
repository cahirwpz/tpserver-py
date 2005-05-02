
from config import db, netlib

from SQL import *
from Message import Message

class Resource(SQLBase):
	tablename = "`resource`"

	def to_packet(self, sequence):
		return netlib.objects.Resource(sequence, self.id, self.name_singular, self.name_pludesc, Message.number(self.id))

	def id_packet(cls):
		return netlib.objects.Resource_IDSequence
	id_packet = classmethod(id_packet)

	def __str__(self):
		return "<Resource id=%s>" % (self.id)

