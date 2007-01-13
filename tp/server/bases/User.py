"""\
Resources require to build stuff.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.db import dbconn
from tp import netlib
from SQL import SQLBase

class User(SQLBase):
	table = Table('user',
		Column('id',	    Integer,     nullable=False, index=True, primary_key=True),
		Column('username',  String(255), nullable=False, index=True),
		Column('password',  String(255), nullable=False, index=True),
		Column('comment',   Binary,      nullable=False),
		Column('time',	    DateTime,    nullable=False, index=True, onupdate=func.current_timestamp()),

		UniqueConstraint('username')
	)

	def usernameid(username, password=None):
		print dbconn

		t = User.table
		if password != None:
			result = dbconn.execute(select([t.c.id], (t.c.username==username) & (t.c.password==password))).fetchall()
		else:
			result = dbconn.execute(select([t.c.id], t.c.username==username)).fetchall()
		
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

