"""\
Research
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp.server.db import *
from tp import netlib
from tp.server.bases.SQL import SQLTypedBase, SQLTypedTable, NoSuch

class Research(SQLTypedBase):
	table = Table('dronesec_research', metadata,
		Column('game', 	       Integer,  nullable=False, index=True, primary_key=True),
		Column('id',	       Integer,  nullable=False, index=True, primary_key=True),
		Column('type',	    String(255), nullable=False, index=True),
		Column('name',         Binary,   nullable = False),
		Column('abbrev',       Binary,   nullable=False, default = ''),
		Column('cost',         Integer,   nullable= False, default= 0),
		Column('reqs',         PickleType,   nullable=False, default = []),
		Column('desc',         Binary,   nullable=False, default = ''),
		Column('time',	    DateTime,    nullable=False, index=True,
			onupdate=func.current_timestamp(), default=func.current_timestamp()),

		ForeignKeyConstraint(['game'], ['game.id']),
	)
	table_extra = SQLTypedTable('dronesec_research')

	@classmethod
	def byname(cls, abbrev):
		c = cls.table.c
		try:
			return select([c.id], c.abbrev == abbrev, limit=1).execute().fetchall()[0]['id']
		except IndexError:
			raise NoSuch("No object with abbreviation) %s" % name)

	@classmethod
	def bytype(cls, type):
		"""\
		bytype(id)

		Returns the objects which have a certain type.
		"""
		t = cls.table

		# FIXME: Need to figure out what is going on here..
		results = select([t.c.id], (t.c.type==bindparam('type'))).execute(type=type).fetchall()
		return [(x['id']) for x in results]

	@classmethod
	def bylist(cls, res):
		"""\
		byreq(abbrev)

		Returns the objects which contain this research abbrev as a requirement
		"""
		c = cls.table.c
		results = select([c.id], not_(c.id.in_(res))).execute().fetchall()
		return [(x['id']) for x in results]




	def __str__(self):
		return "<Research id=%s, name=%s, abbrev =%s>" % (self.id, self.name, self.abbrev)
