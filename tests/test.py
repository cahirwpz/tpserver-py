#!/usr/bin/env python

import textwrap, glob, os.path, copy, fnmatch
from collections import Mapping, MutableMapping

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python.failure import Failure

from tp.server.logging import msg, err, logctx

class TestContext( MutableMapping ):#{{{
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
#}}}

class TestCase( object ):#{{{
	__testpath__ = []

	def __init__( self, ctx = None ):
		self.ctx	= ctx or TestContext()
		self.status = True
		self.reason = None
		self.result = Deferred()
		self.failure = None

		self.__finishing = False

	@logctx
	def __setUpWrapper( self ):
		try:
			methods = []

			for cls in reversed( self.__class__.__mro__ ):
				method = getattr( cls, 'setUp', None )

				if method:
					if not len( methods ) or method != methods[-1]:
						methods.append( method )

			for method in methods:
				method( self )
		except:
			self.failure = Failure()
			self.status  = False
			self.reason  = "SetUp method failed!"

			self.__tearDownWrapper()
		else:
			reactor.callLater( 0, self.run )

	@logctx
	def __tearDownWrapper( self ):
		try:
			methods = []

			for cls in reversed( self.__class__.__mro__ ):
				method = getattr( cls, 'tearDown', None )

				if method:
					if not len( methods ) or method != methods[0]:
						methods.insert( 0, method )

			for method in methods:
				method( self )
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
		self.__setUpWrapper()

	def succeeded( self ):
		assert self.__finishing is False, "Methods 'succeeded' and 'failed' can be called only once!"

		self.__finishing = True

		self.status = True
		reactor.callLater( 0, self.__tearDownWrapper )

	def failed( self, reason ):
		assert self.__finishing is False

		self.__finishing = True

		self.status = False
		self.reason = reason
		reactor.callLater( 0, self.__tearDownWrapper )
	
	def report( self, part = 'all' ):
		if not self.status:
			if part in [ 'prologue', 'all' ]:
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
			if len( self.__testpath__ ):
				return ".".join( self.__testpath__ )
			else:
				return self.__name__
		except AttributeError:
			return self.__class__.__name__
#}}}

class TestSuite( Mapping, TestCase ):#{{{
	def __init__( self, ctx = None ):
		super( TestSuite, self ).__init__( ctx = ctx )

		self.__tests = []
		self.__names = {}
		self.__iter  = None

		self.__failedTest = []

		try:
			tests = self.__tests__
		except AttributeError:
			pass
		else:
			self.addTest( *tests )
	
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

				if issubclass( cls, TestSuite ):
					name = cls.__dict__[ '__name__' ]
				else:
					name = cls.__name__

				cls.__parent__ = self
				cls.__testpath__ = copy.copy( self.__testpath__ )
				cls.__testpath__.append( name )

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
		else:
			self.ctx.restore()

		try:
			while True:
				TestType = self.__iter.next()
				TestName = TestType.__dict__.get( '__name__', TestType.__name__ )
				
				if fnmatch.fnmatch( TestName, self.path_head ):
					break
		except StopIteration:
			if len( self.__failedTest ):
				self.failed( "%s test failed!" % self.__failedTest )
			else:
				self.succeeded()
		else:
			self.ctx.save()
			test = TestType( ctx = self.ctx )
			test.result.addCallbacks( self.__succeeded, self.__failed )

			if isinstance( test, TestSuite ):
				test.start( self.path_tail )
			else:
				test.start()

	@logctx
	def __succeeded( self, test ):
		if isinstance( test, TestSuite ):
			msg( "${grn1}Test suite %s succeeded!${coff}" % test.logPrefix(), level = 'notice' )
		else:
			msg( "${grn1}Test %s succeeded!${coff}" % test.__class__.__name__, level = 'notice' )

		self.run()

	@logctx
	def __failed( self, failure ):
		test = failure.value

		if isinstance( test, TestSuite ):
			msg( "${red1}Test suite %s failed!${coff}" % test.logPrefix(), level = 'error' )
		else:
			msg( "${red1}Test %s failed!${coff}" % test.__class__.__name__, level = 'error' ) 

		self.__failedTest.append( test )
		self.run()

	@logctx
	def start( self, path = "*" ):
		try:
			self.path_head, self.path_tail = path.split('.', 1 )
		except ValueError:
			self.path_head, self.path_tail = path, "*"

		super( TestSuite, self ).start()

	def report( self ):
		if not self.status:
			if self.failure:
				msg( "${red1}----=[ ERROR REPORT START ]=-----${coff}", level='error' )
				msg( "${red1}Reason:${coff}\n %s" % self.reason, level='error' ) 
				msg( "${red1}Traceback:${coff}", level='error' )
				err( _stuff = self.failure )
				msg( "${red1}-----=[ ERROR REPORT END ]=------${coff}", level='error' )

	def getListing( self, depth = 0 ):
		"""
		Retrieves report of all available tests.
		"""

		textwrapper = textwrap.TextWrapper()
		textwrapper.initial_indent = ' ' * 4
		textwrapper.subsequent_indent = ' ' * 11
		textwrapper.width = 100

		report = []
		number = 0

		if depth == 0:
			report.append( '${cyn0}Available test cases list:${coff}' )

		for name, cls in sorted( self.__names.iteritems() ):
			if len( cls.__testpath__[1:] ):
				name = ".".join( cls.__testpath__[1:] )
			else:
				name = cls.__dict__.get( '__name__' )

			if issubclass( cls, TestSuite ):
				subreport, contains = cls().getListing( depth + 1 )

				report += subreport
				number += contains
			else:
				report.append( '  ${wht1}%s:${coff}' % name )

				words = str( cls.__doc__ ).split()

				report += textwrapper.wrap( '${yel0}info:${coff}  %s' % ' '.join( words ) )

				number += 1

		if depth == 0:
			report.append( '${cyn0}Available test cases count: %d${coff}' % number )
			return report

		return report, number
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
			except ImportError, ex:
				msg( "${yel1}Could not import %s!${coff}" % moduleName, level = 'warning' )
				err()
#}}}

__all__ = [ 'TestCase', 'TestSuite', 'TestLoader', 'TestContext' ]
