
from config import db, netlib
from SQL import *

class User(SQLBase):
	tablename = "`user`"

	def usernameid(username, password=None):
		print db
		if password != None:
			result = db.query("""SELECT id FROM %(tablename)s WHERE username="%(username)s" and password="%(password)s" """, username=username, password=password, tablename=User.tablename)
		else:
			result = db.query("""SELECT id FROM %(tablename)s WHERE username="%(username)s" """, username=username, tablename=User.tablename)
		
		if len(result) != 1:
			return -1
		else:
			return result[0]['id']
	usernameid = staticmethod(usernameid)

	def realid(cls, user, pid):
		if pid == 0:
			return user.id
		return pid
	realid = classmethod(realid)

	def __str__(self):
		return "<User id=%s username=%s>" % (self.id, self.username)

	def domain(self):
		return self.username.split("@")[1]

	def to_packet(self, sequence):
		# Preset arguments
		args = [sequence, self.id, self.username, ""]
		return netlib.objects.Player(*args)
	
