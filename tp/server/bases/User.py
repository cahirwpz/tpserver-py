
import db
from SQL import *

class User(SQLBase):
	tablename = "tp.user"

	def realid(username, password=None):
		if password != None:
			result = db.query("""SELECT id FROM tp.user WHERE username="%(username)s" and password="%(password)s" """, username=username, password=password)
		else:
			result = db.query("""SELECT id FROM tp.user WHERE username="%(username)s" """, username=username)
		
		if len(result) != 1:
			return -1
		else:
			return result[0]['id']
	realid = staticmethod(realid)

	def __str__(self):
		return "<User id=%s username=%s>" % (self.id, self.username)

