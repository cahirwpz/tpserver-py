#!/usr/bin/env python

import glob, os.path, copy, unittest, sys
from logging import debug, exception
from collections import MutableMapping

from tp.server.logger import logctx

class TestContext( MutableMapping ):
	def __init__( self ):
		super( TestContext, self ).__init__()

		self.__stack = []
		self.__data  = {}

	def save( self ):
		self.__stack.append( self.__data )
		self.__data = copy.copy( self.__data )

	def restore( self ):
		self.__data = self.__stack.pop()
	
	def __getitem__( self, key ):
		return self.__data.__getitem__( key )

	def __setitem__( self, key, value ):
		self.__data.__setitem__( key, value )

	def __delitem__( self, key ):
		self.__data.__delitem__( key )

	def __len__( self ):
		return self.__data.__len__()

	def __iter__( self ):
		return self.__data.__iter__()

	def __contains__( self, key ):
		return self.__data.__contains__( key )

class TestCase( unittest.TestCase ):
	def __init__( self, ctx ):
		unittest.TestCase.__init__( self )
		
		self.ctx = ctx

	@property
	def model( self ):
		return self.ctx['game'].model

	def logPrefix( self ):
		return self.__class__.__name__

class TestSuite( unittest.TestSuite ):
	failureException = AssertionError

	def __init__( self, ctx, tests = [] ):
		unittest.TestSuite.__init__( self, tests )

		self.ctx = ctx

		try:
			tests = self.__tests__
		except AttributeError:
			pass
		else:
			for cls in tests:
				self.addTest( cls( self.ctx ) )

	@property
	def model( self ):
		return self.ctx['game'].model

	def setUp( self ):
		pass

	def tearDown( self ):
		pass

	def defaultTestResult(self):
		return unittest.TestResult()

	@logctx
	def run( self, result = None ):
		if result is None:
			result = self.defaultTestResult()

		result.startTest( self )

		try:
			try:
				self.setUp()
			except KeyboardInterrupt:
				raise
			except:
				result.addError(self, self._exc_info())
				return

			ok = False
			try:
				self.runTest( result )
				ok = True
			except self.failureException:
				result.addFailure(self, self._exc_info())
			except KeyboardInterrupt:
				raise
			except:
				result.addError(self, self._exc_info())

			try:
				self.tearDown()
			except KeyboardInterrupt:
				raise
			except:
				result.addError(self, self._exc_info())
				ok = False
			if ok:
				result.addSuccess(self)
		finally:
			result.stopTest(self)

	def shortDescription( self ):
		return "Test Suite %s" % self.__name__
	
	def runTest( self, _result ):
		self.ctx.save()
		result = unittest.TestSuite.run( self, _result )
		self.ctx.restore()
		return result

	def addTest( self, test ):
		unittest.TestSuite.addTest( self, test )
		debug( "Added %s to %s.", test.__class__.__name__, self.__class__.__name__ )

	def _exc_info(self):
		return sys.exc_info()

	def debug( self ):
		self.setUp()

		for test in self._tests:
			test.debug()

		self.tearDown()

	def logPrefix( self ):
		return self.__class__.__name__

class TestLoader( TestSuite ):
	"""
	Stores and manages all tests.
	"""

	__path__ = None

	def __init__( self ):
		super( TestLoader, self ).__init__( TestContext() )

		path = os.path.dirname( os.path.abspath( __file__ ) )

		for modulePath in sorted( glob.glob( os.path.join( path, self.__path__, '*.py' ) ) ):
			moduleName = os.path.splitext( os.path.basename( modulePath ) )[0]

			try:
				module = __import__( "%s.%s" % ( self.__path__, moduleName ), globals(), locals(), [ moduleName ], -1 )

				try:
					classes = module.__tests__
				except AttributeError:
					classes = []

				for cls in classes:
					self.addTest( cls( self.ctx ) )
			except ImportError, ex:
				exception( "${yel1}Could not import %s!${coff}" % moduleName )

__all__ = [ 'TestCase', 'TestSuite', 'TestLoader', 'TestContext' ]
