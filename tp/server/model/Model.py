#!/usr/bin/env python

from SQL import SQLBase
from DatabaseManager import DatabaseManager

class Model( object ):#{{{
	@staticmethod
	def add( *objs ):
		objs = filter( lambda x: x is not None, objs )

		assert all( isinstance( obj, SQLBase ) for obj in objs )
		
		with DatabaseManager().session() as session:
			for obj in objs:
				session.add( obj )

	@staticmethod
	def remove( *objs ):
		objs = filter( lambda x: x is not None, objs )

		assert all( isinstance( obj, SQLBase ) for obj in objs )

		with DatabaseManager().session() as session:
			for obj in objs:
				obj.remove( session )

	@staticmethod
	def refresh( *objs ):
		objs = filter( lambda x: x is not None, objs )

		assert all( isinstance( obj, SQLBase ) for obj in objs )
		
		with DatabaseManager().session() as session:
			for obj in objs:
				session.refresh( obj )

	@staticmethod
	def query( cls ):
		return DatabaseManager().query( cls )
#}}}

import sqlalchemy

or_  = sqlalchemy.or_
and_ = sqlalchemy.and_

__all__ = [ 'Model', 'or_', 'and_' ]
