
from config import db, netlib

from SQL import *

class Category(SQLBase):
	tablename = "`category`"

	def realid(id, pid):
		return id
	realid = staticmethod(realid)

	def to_packet(self, sequence):
		# Preset arguments
		return netlib.objects.Category(sequence, self.id, self.name, self.desc)

	def __str__(self):
		return "<Category id=%s name=%s>" % (self.id, self.name)

