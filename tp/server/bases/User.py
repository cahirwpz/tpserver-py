
from config import db
from SQL import *

class User(SQLBase):
	tablename = "`user`"

	def realid(username, password=None):
		print db
		if password != None:
			result = db.query("""SELECT id FROM %(tablename)s WHERE username="%(username)s" and password="%(password)s" """, username=username, password=password, tablename=User.tablename)
		else:
			result = db.query("""SELECT id FROM %(tablename)s WHERE username="%(username)s" """, username=username, tablename=User.tablename)
		
		if len(result) != 1:
			return -1
		else:
			return result[0]['id']
	realid = staticmethod(realid)

	def __str__(self):
		return "<User id=%s username=%s>" % (self.id, self.username)

	def domain(self):
		return self.username.split("@")[1]
