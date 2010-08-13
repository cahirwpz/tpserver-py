#!/usr/bin/env python

from SQL import SQLBase
from DatabaseManager import DatabaseManager

def flatten( x ):#{{{
    result = []

    for el in x:
        if hasattr( el, "__iter__") and not isinstance( el, basestring ):
            result.extend( flatten( el ) )
        else:
            result.append( el )

    return result
#}}}

class Model( object ):#{{{
	@staticmethod
	def add( *objs ):
		objs = filter( lambda x: x is not None, flatten( objs ) )

		assert all( isinstance( obj, SQLBase ) for obj in objs )
		
		with DatabaseManager().session() as session:
			for obj in objs:
				session.add( obj )

	@staticmethod
	def remove( *objs ):
		objs = filter( lambda x: x is not None, flatten( objs ) )

		assert all( isinstance( obj, SQLBase ) for obj in objs )

		with DatabaseManager().session() as session:
			for obj in objs:
				obj.remove( session )

	@staticmethod
	def refresh( *objs ):
		objs = filter( lambda x: x is not None, flatten( objs ) )

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
