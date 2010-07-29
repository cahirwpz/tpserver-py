#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation

from tp.server.model import SQLBase, SelectableByName

class Ship( SQLBase, SelectableByName ):	
	@classmethod
	def InitMapper( cls, metadata, Design ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',             Integer, index = True, primary_key = True ),
				Column('design_id',      ForeignKey( Design.id ), index = True, nullable = False ),
				Column('hp',             Integer, nullable = False ),
				Column('primary_damage', Integer, nullable = False ),
				Column('backup_damage',  Integer, nullable = False ),
				Column('backup_damage',  Integer, nullable = False ),
				Column('speed',          Integer, nullable = False ),
				Column('build_time',     Integer, nullable = False ))

		mapper( cls, cls.__table__, properties = {
			'design': relation( Design,
				uselist = False )
			})
