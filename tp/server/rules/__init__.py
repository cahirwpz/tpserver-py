import os.path, traceback, inspect
from collections import Mapping

from tp.server.singleton import SingletonContainerClass
from tp.server.rules.base import Ruleset

class RulesetManager( Mapping ):
	__metaclass__ = SingletonContainerClass

	def __init__( self ):
		path = os.path.dirname( os.path.abspath( __file__ ) )

		self.__ruleset = {}

		for name in os.listdir( path ):
			if name != "base" and os.path.isdir( os.path.join( path, name ) ):
				try:
					ruleset = __import__( "%s.%s" % ( __package__, name ), globals(), locals(), [ name ], -1 )

					for name, cls in inspect.getmembers( ruleset, lambda o: inspect.isclass(o) ):
						if issubclass( cls, Ruleset ) and cls is not Ruleset:
							self.__ruleset[ cls.name ] = cls
				except ImportError, msg:
					traceback.print_exc()
					print "\033[31;1mDisabling %s ruleset!\033[0m" % name
	
	def __getitem__( self, name ):
		return self.__ruleset[ name ]

	def __iter__( self ):
		return self.__ruleset.__iter__()

	def __len__( self ):
		return self.__ruleset.__len__()

__all__ = [ 'RulesetManager' ]
