import os.path

from tp.server.singleton import SingletonClass

class RulesetManager( object ):
	__metaclass__ = SingletonClass

	def __init__( self ):
		path = os.path.dirname( os.path.abspath( __file__ ) )

		self.ruleset = {}

		for name in os.listdir( path ):
			if name != "base" and os.path.isdir( os.path.join( path, name ) ):
				try:
					ruleset = __import__( "%s.%s" % ( __package__, name ), globals(), locals(), [ name ], -1 )

					self.ruleset[ ruleset.__name__.split('.')[-1] ] = ruleset.Ruleset
				except ImportError, msg:
					print "Could not import %s: %s" % ( name, msg )

__all__ = [ 'RulesetManager' ]
