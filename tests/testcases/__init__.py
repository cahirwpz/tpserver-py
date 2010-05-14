import inspect, glob, os.path

__testcases__ = []

if __name__ == __package__:
	path = os.path.dirname( os.path.abspath( __file__ ) )

	for modulePath in glob.glob( os.path.join( path, '*.py' ) ):
		moduleName = os.path.splitext( os.path.basename( modulePath ) )[0]

		try:
			module = __import__( "%s.%s" % ( __package__, moduleName ), globals(), locals(), [ moduleName ], -1 )
			classes = inspect.getmembers( module, inspect.isclass )
			classes = filter( lambda c: c[1].__module__.startswith( "%s." % __package__ ), classes )
			classes = filter( lambda c: hasattr( c[1], "description" ), classes )

			__testcases__.extend( _type for _name, _type in classes )
		except ImportError, msg:
			print "Could not import %s: %s" % ( moduleName, msg )

