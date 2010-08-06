#!/usr/bin/env python

import textwrap, glob, os.path
from collections import Mapping

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python.failure import Failure

from tp.server.logging import msg, err, logctx

class TestCase( object ):#{{{
	def __init__( self ):
		self.status = True
		self.reason = None
		self.result = Deferred()
		self.failure = None

	@logctx
	def __setUp( self ):
		try:
			self.setUp()
		except Exception:
			self.failure = Failure()
			self.status  = False
			self.reason  = "SetUp method failed!"

			self.__tearDown()
		else:
			reactor.callLater( 0, self.run )

	@logctx
	def __tearDown( self ):
		try:
			self.tearDown()
		except Exception:
			if self.status:
				self.failure = Failure()
				self.status  = False
				self.reason  = "TearDown method failed!"

		self.report()

		if self.status:
			self.result.callback( self )
		else:
			self.result.errback( self )

	def setUp( self ):
		pass

	@logctx
	def run( self ):
		self.succeeded()

	def tearDown( self ):
		pass

	@logctx
	def start( self ):
		self.__setUp()

	def succeeded( self ):
		self.status = True
		reactor.callLater( 0, self.__tearDown )

	def failed( self, reason ):
		self.status = False
		self.reason = reason
		reactor.callLater( 0, self.__tearDown )
	
	def report( self, part = 'all' ):
		if self.status:
			msg( "${grn1}Test %s succeeded!${coff}" % self.__class__.__name__, level = 'notice' )
		else:
			if part in [ 'prologue', 'all' ]:
				msg( "${red1}Test %s failed!${coff}" % self.__class__.__name__, level = 'error' ) 
				msg( "${red1}----=[ ERROR REPORT START ]=-----${coff}", level='error' )
				msg( "${red1}Test name:${coff}\n %s" % self.__class__.__name__, level='error' ) 
				msg( "${red1}Description:${coff}\n %s" % self.__doc__.strip(), level='error' ) 
				msg( "${red1}Reason:${coff}\n %s" % self.reason, level='error' ) 

			if part in [ 'epilogue', 'all' ]:
				if self.failure:
					err( _stuff = self.failure )
				msg( "${red1}-----=[ ERROR REPORT END ]=------${coff}", level='error' )

	def logPrefix( self ):
		try:
			return self.__parent__.__name__
		except AttributeError:
			return self.__class__.__name__
#}}}

class TestSuite( Mapping, TestCase ):#{{{
	def __init__( self ):
		super( TestSuite, self ).__init__()

		self.__tests = []
		self.__names = {}
		self.__iter  = None

		self.__failedTest = []
	
	def setUp( self ):
		msg( "${cyn1}Setting up %s test suite...${coff}" % self.__class__.__name__, level='info' ) 
	
	def tearDown( self ):
		msg( "${cyn1}Tearing down %s test suite...${coff}" % self.__class__.__name__, level='info' ) 

	def addTest( self, *args ):
		for cls in args:
			if cls in self.__tests:
				msg( '${yel1}Test of type %s already registered!${coff}' % cls.__name__ )
			else:
				self.__tests.append( cls )
				self.__names[ cls.__name__ ] = cls

				cls.__parent__ = self

	def __getitem__( self, name ):
		return self.__names[ name ]

	def __len__( self ):
		return self.__names.__len__()

	def __iter__( self ):
		return self.__names.iterkeys()

	def __contains__( self, test ):
		if issubclass( test, TestCase ):
			return test in self.__tests

		return test in self.__names

	def run( self ):
		if not self.__iter:
			self.__iter = iter( self.__tests )

		try:
			TestType = self.__iter.next()
		except StopIteration:
			if len( self.__failedTest ):
				self.failed( "%s test failed!" % self.__failedTest )
			else:
				self.succeeded()
		else:
			test = TestType()
			test.result.addCallbacks( self.__succeeded, self.__failed )
			test.start()

	def __succeeded( self, test ):
		self.run()

	def __failed( self, failure ):
		self.__failedTest.append( failure.value )
		self.run()

	def report( self ):
		if not self.status:
			msg( "${red1}Test suite %s failed!${coff}" % self.__class__.__name__, level = 'error' ) 
			if self.failure:
				msg( "${red1}----=[ ERROR REPORT START ]=-----${coff}", level='error' )
				msg( "${red1}Reason:${coff}\n %s" % self.reason, level='error' ) 
				msg( "${red1}Traceback:${coff}", level='error' )
				err( _stuff = self.failure )
				msg( "${red1}-----=[ ERROR REPORT END ]=------${coff}", level='error' )

	def getListing( self ):
		"""
		Retrieves report of all available tests.
		"""

		textwrapper = textwrap.TextWrapper()
		textwrapper.initial_indent = ' ' * 4
		textwrapper.subsequent_indent = ' ' * 11
		textwrapper.width = 100

		report = []

		report.append( '${cyn0}Available test cases list:${coff}' )

		for name, cls in sorted( self.__names.iteritems() ):
			report.append( '  ${wht1}%s:${coff}' % name )

			words = str( cls.__doc__ ).split()

			report += textwrapper.wrap( '${yel0}info:${coff}  %s' % ' '.join( words ) )

		report.append( '${cyn0}Available test cases count: %d${coff}' % len( self ) )

		return report

	def logPrefix( self ):
		try:
			return self.__name__
		except AttributeError:
			return self.__class__.__name__
#}}}

class TestLoader( TestSuite ):#{{{
	"""
	Stores and manages all tests.
	"""

	__path__ = None

	def __init__( self ):
		super( TestLoader, self ).__init__()

		path = os.path.dirname( os.path.abspath( __file__ ) )

		for modulePath in sorted( glob.glob( os.path.join( path, self.__path__, '*.py' ) ) ):
			moduleName = os.path.splitext( os.path.basename( modulePath ) )[0]

			try:
				module = __import__( "%s.%s" % ( self.__path__, moduleName ), globals(), locals(), [ moduleName ], -1 )

				try:
					classes = module.__tests__
				except AttributeError:
					classes = []

				self.addTest( *classes )
			except ImportError, msg:
				msg( "${yel1}Could not import %s: %s!${coff}" % ( moduleName, msg ), level = 'warning' )
				err()
#}}}

__all__ = [ 'TestCase', 'TestSuite', 'TestLoader' ]
