#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from tp.server.bases import SQLBase

class FleetComposition( SQLBase ):	
	@classmethod
	def InitMapper( cls, metadata, Fleet, Ship ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('fleet_id', ForeignKey( Fleet.id ), primary_key = True ),
				Column('ship_id',  ForeignKey( Ship.id ), primary_key = True ),
				Column('number',   Integer, nullable = False ))

		cols = cls.__table__.c

		Index('ix_%s_fleet_ship' % cls.__tablename__, cols.fleet_id, cols.ship_id)

		mapper( cls, cls.__table__, properties = {
			'fleet': relation( Fleet,
				uselist = False,
				backref = backref( 'ships' ),
				cascade = 'all'),
			'ship': relation( Ship,
				uselist = False,
				cascade = 'all')
			})
