import inspect, glob, os.path, textwrap
from collections import MutableSet, Mapping

class TestManager( MutableSet, Mapping ):#{{{
	"""
	Stores and manages all tests.
	"""
	def __init__( self ):
		self.__tests = set()
		self.__nameToTest = {}
	
	def loadTests( self ):
		path = os.path.dirname( os.path.abspath( __file__ ) )

		for modulePath in glob.glob( os.path.join( path, '*.py' ) ):
			moduleName = os.path.splitext( os.path.basename( modulePath ) )[0]

			try:
				module = __import__( "%s.%s" % ( __package__, moduleName ), globals(), locals(), [ moduleName ], -1 )

				try:
					classes = module.__tests__
				except AttributeError:
					classes = []

				for _type in classes:
					self.add( _type )
			except ImportError, msg:
				print "Could not import %s: %s" % ( moduleName, msg )

	def add( self, _type ):
		_name = _type.__name__

		if _type in self.__tests:
			print( 'Test of type %s already registered!' % _name )
			return

		if _name in self.__nameToTest.keys():
			print( 'Test named %s already registered!' % _name )
			return

		self.__tests.add( _type )
		self.__nameToTest[ _name ] = _type

	def discard( self, testType ):
		if testType not in self.__tests:
			raise ValueError( 'test of type %s not registered' % testType.__name__ )

		self.__test.discard( testType )
		del self.__nameToTest[ testType ]

	def __getitem__( self, _name ):
		return self.__nameToTest[ _name ]
	
	def __len__( self ):
		return self.__tests.__len__()

	def __iter__( self ):
		return self.__nameToTest.iterkeys()

	def __contains__( self, test ):
		return test in self.__test

	def getReport( self ):
		"""
		Retrieves report of all available tests.
		"""

		textwrapper = textwrap.TextWrapper()
		textwrapper.initial_indent = ' ' * 4
		textwrapper.subsequent_indent = ' ' * 11
		textwrapper.width = 100

		report = []

		report.append( '${cyn0}Available test cases list:${coff}' )

		for testName, testType in sorted( self.__nameToTest.iteritems() ):
			report.append( '  ${wht1}%s:${coff}' % testName )

			words = str( testType.__doc__ ).split()

			report += textwrapper.wrap( '${yel0}info:${coff}  %s' % ' '.join( words ) )

		report.append( '${cyn0}Available test cases count: %d${coff}' % len( self ) )

		return report
#}}}

__manager__ = None

if __name__ == __package__:
	__manager__= TestManager()
	__manager__.loadTests()
