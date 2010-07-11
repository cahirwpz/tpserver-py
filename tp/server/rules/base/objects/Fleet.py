#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from tp.server.bases import Attribute

from tp.server.rules.base.parameters import PlayerParam, DesignListParam, NumberParam

class FleetAttributes( object ):
	owner = Attribute(
			type		= PlayerParam,
			level		= 'public',
			description	= "Owner of the fleet." )

	ships = Attribute(
			type		= DesignListParam,
			level		= 'protected',
			description	= "Listing of ships in the fleet.")

	damage = Attribute(
			type		= NumberParam,
			level		= 'protected',
			description = "How much in HP is the fleet damaged.")

class Fleet( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Object, Player ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column( 'object_id', ForeignKey( Object.id ), index = True, primary_key = True ),
				Column( 'owner_id',  ForeignKey( Player.id ), nullable = True ))

		mapper( cls, cls.__table__, inherits = Object, polymorphic_identity = 'Fleet', properties = {
			'owner' : relation( Player,
				uselist = False,
				backref = backref( 'fleets' ),
				cascade = 'all')
			})

	@property
	def typeno( self ):
		return 4
#}}}

__all__ = [ 'Fleet' ]
