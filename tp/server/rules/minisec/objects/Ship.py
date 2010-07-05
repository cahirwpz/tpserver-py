#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from tp.server.bases import SQLBase, SelectableByName

class Ship( SQLBase, SelectableByName ):	
	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',             Integer, primary_key = True ),
				Column('name',           String(255), nullable = False ),
				Column('hp',             Integer, nullable = False ),
				Column('primary_damage', Integer, nullable = False ),
				Column('backup_damage',  Integer, nullable = False ),
				Column('backup_damage',  Integer, nullable = False ),
				Column('speed',          Integer, nullable = False ))

		mapper( cls, cls.__table__ )
