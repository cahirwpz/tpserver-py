#!/usr/bin/env python

from collections import Iterator

class TestCase( object ):#{{{
	def setUp( self ):
		pass

	def tearDown( self ):
		pass

	def __call__( self ):
		pass
#}}}

class TestSuite( TestCase, Iterator ):#{{{
	def __init__( self ):
		self.__tests = []

	def addTest( self, *args ):
		for cls in args:
			self.__tests.append( cls )

	def next( self ):
		try:
			return self.__tests.pop(0)
		except IndexError:
			raise StopIteration
#}}}

__all__ = [ 'TestCase', 'TestSuite' ]
