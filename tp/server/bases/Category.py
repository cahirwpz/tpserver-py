
from config import db, netlib

from SQL import *

class Category(SQLBase):
	tablename = "`category`"

	def to_packet(self, sequence):
		# Preset arguments
		return netlib.objects.Category(sequence, self.id, self.name, self.desc)

	def __str__(self):
		return "<Category id=%s name=%s>" % (self.id, self.name)

