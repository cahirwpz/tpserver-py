#!/usr/bin/env python

from twisted.internet.defer import Deferred

from tp.server.logging import msg

class TestCase( object ):#{{{
	def __init__( self ):
		self.status = True
		self.reason = None
		self.result = Deferred()

	def setUp( self ):
		pass

	def tearDown( self ):
		pass

	def run( self ):
		raise NotImplementedError

	def __call__( self ):
		self.run()

	def succeeded( self ):
		self.status = True
		self.result.callback( self )

	def failed( self, reason ):
		self.status = False
		self.reason = reason
		self.result.errback( self )

	def logPrefix( self ):
		try:
			return self.parent.__name__
		except AttributeError:
			return self.__class__.__name__
#}}}

class TestSuite( TestCase ):#{{{
	def __init__( self ):
		super( TestSuite, self ).__init__()

		self.__tests = []
		self.__index = 0
	
	def setUp( self ):
		msg( "${cyn1}Setting up %s test suite...${coff}" % self.__class__.__name__, level='info' ) 
	
	def tearDown( self ):
		msg( "${cyn1}Tearing down %s test suite...${coff}" % self.__class__.__name__, level='info' ) 

	def addTest( self, *args ):
		for cls in args:
			self.__tests.append( cls )

	def run( self ):
		if self.__index >= len( self.__tests ):
			if self.result:
				self.result.callback( self )
			else:
				self.result.errback( self )
		else:
			TestType = self.__tests[ self.__index ]
			TestType.parent = self

			self.__index += 1

			test = TestType()
			test.result.addCallbacks( self.__succeeded, self.__failed )
			test.setUp()
			test.run()

	def __succeeded( self, test ):
		test.tearDown()
		self.run()

	def __failed( self, failure ):
		self.status = False
		self.reason = "One or more tests failed!"

		test = failure.value
		test.tearDown()
		self.run()
#}}}

__all__ = [ 'TestCase', 'TestSuite' ]
