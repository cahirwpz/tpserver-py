#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from Model import ModelObject

class Player( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',	    Integer, index = True, primary_key = True),
				Column('username',  String(255), nullable = False, ),
				Column('password',  String(255), nullable = False, ),
				Column('email',     String(255), nullable = True ),
				Column('comment',   Text, nullable = False, default = ""),
				Column('mtime',	    DateTime, nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()),
				UniqueConstraint('username'))

		mapper( cls, cls.__table__ )

	@classmethod
	def ByName( cls, username, password = None ):
		"""
		Get the id for a user given a game, username and password.
		"""
		if password is None:
			return cls.query().filter_by( username = username ).first()
		else:
			return cls.query().filter_by( username = username, password = password ).first()

	def __str__(self):
		return '<%s@%s id="%s" username="%s">' % ( self.__origname__, self.__game__.name, self.id, self.username )

__all__ = [ 'Player' ]
