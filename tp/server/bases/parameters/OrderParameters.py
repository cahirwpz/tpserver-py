#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

class AbsCoordParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('x',         Integer, nullable = False ),
				Column('y',         Integer, nullable = False ),
				Column('z',         Integer, nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'AbsCoord' )
#}}}

class TimeParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('turns',     Integer, nullable = False ),
				Column('max',       Integer, nullable = True ),
				CheckConstraint( 'turns >= 0 and turns <= max', name = 'turns in [0, max]' ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'Time' )
#}}}

class ObjectParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, Object ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('object_id', ForeignKey( Object.id ), nullable = True ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'Object' )
#}}}

class PlayerParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, Player ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('player_id', ForeignKey( Player.id ), index = True, nullable = False ),
				Column('mask',      Integer, nullable = False ),
				CheckConstraint( 'mask >= 0 and mask < 16', name = 'mask in [0,15]' ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'Player', properties = {
			'player' : relation( Player,
				uselist = False )
			})
#}}}

class RelCoordParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, Object ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',  ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('x',         Integer, nullable = False ),
				Column('y',         Integer, nullable = False ),
				Column('z',         Integer, nullable = False ),
				Column('parent_id', ForeignKey( Object.id ), nullable = True ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'RelCoord', properties = {
			'parent' : relation( Object,
				uselist = False )
			})
#}}}

class RangeParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id', ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('value',    Integer, nullable = False ),
				Column('min',      Integer, nullable = False ),
				Column('max',      Integer, nullable = False ),
				Column('step',     Integer, nullable = False ),
				CheckConstraint( 'min < max' ),
				CheckConstraint( 'value >= min and value <= max' ),
				CheckConstraint( 'step < max - min' ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'Range' )
#}}}

class SelectionListParam( object ):#{{{
	@classmethod
	def InitMapper( cls, metadata, Parameter, SelectionList ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id', ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('list_id',  ForeignKey( SelectionList.id ), nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'SelectionList', properties = {
			'selections' : relation( SelectionList,
				cascade = 'all',
				collection_class = list )
			})
#}}}

class StringParam( object ):#{{{
	# TODO: constraint checking!
	#  - 'value' string must be shorter than 'max' characters
	@classmethod
	def InitMapper( cls, metadata, Parameter ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id', ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('value',    Text, nullable = False ),
				Column('max',      Integer, nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'String' )
#}}}

class ReferenceParam( object ):#{{{
	# TODO: constraint checking!
	# - 'reference' must be present in 'allowed' list
	# - 'allowed' list items must be unique
	@classmethod
	def InitMapper( cls, metadata, Parameter, NumberList ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',        ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('reference',       Integer, nullable = False ),
				Column('allowed_list_id', ForeignKey( NumberList.id ), nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'Reference', properties = {
			'allowed' : relation( NumberList,
				primaryjoin = cls.__table__.c.allowed_list_id == NumberList.__table__.c.id,
				cascade = 'all',
				collection_class = set )
			})
#}}}

class ReferenceListParam( object ):#{{{
	# TODO: constraint checking!
	#  - 'references' list items must be present in 'allowed' list
	#  - 'allowed' list items must be unique
	@classmethod
	def InitMapper( cls, metadata, Parameter, NumberList ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('param_id',          ForeignKey( Parameter.id ), index = True, primary_key = True ),
				Column('reference_list_id', ForeignKey( NumberList.id ), nullable = False ),
				Column('allowed_list_id',   ForeignKey( NumberList.id ), nullable = False ))

		mapper( cls, cls.__table__, inherits = Parameter, polymorphic_identity = 'ReferenceList', properties = {
			'references' : relation( NumberList,
				primaryjoin = cls.__table__.c.reference_list_id == NumberList.__table__.c.id,
				cascade = 'all',
				collection_class = list ),
			'allowed' : relation( NumberList,
				primaryjoin = cls.__table__.c.allowed_list_id == NumberList.__table__.c.id,
				cascade = 'all',
				collection_class = set )
			})
#}}}

MissingOrderParameters  = [ 'ResourceList', 'GenericReferenceQuantityList' ]

__all__ = [ 'AbsCoordParam', 'TimeParam', 'ObjectParam', 'PlayerParam',
			'RelCoordParam', 'RangeParam', 'SelectionListParam',
			'StringParam', 'ReferenceParam', 'ReferenceListParam' ]
