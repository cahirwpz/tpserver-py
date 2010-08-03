#!/usr/bin/env python

import fnmatch

from twisted.internet import reactor

from tp.server.logging import Logger, msg, logctx
from tp.server.configuration import ComponentConfiguration, StringOption, ConfigurationError

from test import TestSuite

class TestSelector( TestSuite ):#{{{
	def __init__( self ):
		super( TestSelector, self ).__init__()

		from testcases import __manager__ as testcases

		for name, cls in testcases.iteritems():
			self.addTest( cls )

	def configure( self, configuration ):
		tests = configuration.tests

		if tests == 'LIST':
			raise SystemExit( Logger.colorizeMessage( '\n'.join( self.__manager.getReport() ) ) )
		elif tests == 'DEFAULT':
			self.__tests = [ 'DEFAULT' ]
		elif tests == 'ALL':
			#self.__tests = self.__manager.keys()
			pass
		else:
			for name in tests.split(','):
				try:
					names = fnmatch.filter( self.__manager.keys(), name )

					if not names:
						raise KeyError( 'No test matching \'%s\'' % name )

					self.__tests.extend( names )
				except KeyError, ex:
					raise SystemExit( ex )

		#if not self.__tests:
		#	raise ConfigurationError( 'test run is empty' )

#}}}

class TestSelectorConfiguration( ComponentConfiguration ):#{{{
	tests = StringOption( short='t', default='ALL',
						  help='Specifies which tests will be added to test run. TEST-LIST is a list of test names or glob (see unix manual pages) patterns separated by comma. There are some arguments to this option that have a special meaning. \'LIST\' will force to display all available tests and finish the application. \'ALL\' will add all available test to test run.', arg_name='TEST-LIST' )
#}}}

class TestRunner( object ):#{{{
	def __init__( self, selector ):
		self.selector = selector
		self.selector.result.addCallbacks( self.__succeeded, self.__failed )
	
	def __succeeded( self, test ):
		reactor.stop()
	
	def __failed( self, failure ):
		reactor.stop()

	def start( self ):
		reactor.callLater( 0, self.selector.run )
	
	def logPrefix( self ):
		return self.__class__.__name__
#}}}

__all__ = [ 'TestRunner', 'TestSelector', 'TestSelectorConfiguration' ]
