"""\
The basis for all objects that exist.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.db import *
from tp import netlib
from tp.server.bases.SQL import SQLBase, SQLTypedBase, SQLTypedTable, quickimport


class Drone(SQLBase):
	table = Table('drone', metadata,
		Column('game',	     Integer,  nullable=False, index=True, primary_key=True),
		Column('id',	     Integer,  nullable=False, index=True, primary_key=True),
		Column('type',	     String(255), nullable=False, index=True),
		Column('name',       Binary,   nullable=False, index=True),
		Column('cost',       Integer,  nullable=False, default=0),
		Column('power',      Integer,  nullable=False, default=0),
		Column('attack',     Integer,  nullable=False, default=0),
		Column('numAttacks', Integer,  nullable=False, default=0),
		Column('health',     Integer,  nullable=False, default=0),
		Column('speed',      Integer,  nullable=False, default=0),
		Column('strength',   Binary,   nullable=False, default = ""),
		Column('weakness',   Binary,   nullable=False, default = ""),
		Column('reqs',       Binary,   nullable=False, default = ""),
		Column('cost',       Integer,  nullable=False, default=0),
		Column('time',	     DateTime, nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),


		UniqueConstraint('id', 'game'),
		ForeignKeyConstraint(['game'],   ['game.id']),
	)

	@classmethod
	def bytype(cls, type):
		"""\
		bytype(id)

		Returns the objects which have a certain type.
		"""
		t = cls.table

		# FIXME: Need to figure out what is going on here..
		results = select([t.c.id, t.c.time], (t.c.type==bindparam('type'))).execute(type=type).fetchall()
		return [(x['id'], x['time']) for x in results]

	@classmethod
	def byreq(cls, req):
		t = cls.table
		results = select([t.c.id, t.c.reqs], (t.c.reqs in bindparam('reqs'))).execute(req=req).fetchall()
		return [(x['id'], x['reqs']) for x in results]



	def __str__(self):
		return "<Drone id=%s>" % (self.id)