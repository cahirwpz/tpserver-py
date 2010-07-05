import os.path
from collections import Mapping

from tp.server.singleton import SingletonContainerClass

class RulesetManager( Mapping ):
	__metaclass__ = SingletonContainerClass

	def __init__( self ):
		path = os.path.dirname( os.path.abspath( __file__ ) )

		self.__ruleset = {}

		for name in os.listdir( path ):
			if name != "base" and os.path.isdir( os.path.join( path, name ) ):
				try:
					ruleset = __import__( "%s.%s" % ( __package__, name ), globals(), locals(), [ name ], -1 )

					self.__ruleset[ ruleset.__name__.split('.')[-1] ] = ruleset.Ruleset
				except ImportError, msg:
					print "Could not import %s: %s" % ( name, msg )
	
	def __getitem__( self, name ):
		return self.__ruleset[ name ]

	def __iter__( self ):
		return self.__ruleset.__iter__()

	def __len__( self ):
		return self.__ruleset.__len__()

__all__ = [ 'RulesetManager' ]
