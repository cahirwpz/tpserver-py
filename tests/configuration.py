#!/usr/bin/env python

"""
Classes related to configuration reading, writing and applying it to components.
"""

import inspect, optparse, textwrap

class ConfigurationError( BaseException ):
	"""
	Configuration error exception.
	
	Raised if configuring a component has failed.
	"""

class Option( object ):
	__name__ = None

	def __init__( self, help, short = None, default = None, arg_name = None ):
		self.short		= short
		self.help		= help
		self.arg_name	= arg_name
		self.default	= default

	def __get__( self, obj, objtype ):
		if obj is None:
			return self

		return self.__value

	def __set__( self, obj, value ):
		self.__value = value
	
	def __str__( self ):
		if not self.__name__:
			return "<%s object at 0x%x>" % ( self.__class__.__name__, id(self) )
		else:
			return "<%s \'%s\' object at 0x%x>" % ( self.__class__.__name__, self.__name__, id(self) )

class BooleanOption( Option ):
	def __init__( self, **kwargs ):
		Option.__init__( self, **kwargs )
	
	def __set__( self, obj, value ):
		if type( value ) is not bool:
			raise ConfigurationError( '%s flag must be a boolean' % self.name )

		Option.__set__( self, obj, value )

class IntegerOption( Option ):
	def __init__( self, min = None, max = None, **kwargs ):
		self.__min = min
		self.__max = max
		Option.__init__( self, **kwargs )
	
	def __set__( self, obj, value ):
		if type( value ) not in [ int, long ]:
			raise ConfigurationError( '%s must be an integer' % self.name )

		if self.__min is not None and value < self.__min:
			raise ConfigurationError( '%s must be greater or equal to' % (self.name, self.__min) )

		if self.__max is not None and value > self.__max:
			raise ConfigurationError( '%s must be less or equal to' % (self.name, self.__max) )

		Option.__set__( self, obj, value )

	@property
	def type( self ):
		return int

class StringOption( Option ):
	def __init__( self, allow_empty = False, **kwargs ):
		self.__allow_empty = allow_empty

		Option.__init__( self, **kwargs )

	def __set__( self, obj, value ):
		if not isinstance( value, ( str, unicode ) ) and not ( self.__allow_empty and value is None ):
			raise ConfigurationError( '%s must be a string' % self.__name__ )

		Option.__set__( self, obj, value )
	
	@property
	def type( self ):
		return str

class StringSetOption( Option ):
	def __init__( self, values, **kwargs ):
		self.__values = values

		Option.__init__( self, **kwargs )

	def __set__( self, obj, value ):
		if not isinstance( value, ( str, unicode ) ):
			raise ConfigurationError( '%s must be a string' % self.name )

		if value not in self.__values:
			raise ConfigurationError( '%s must be one of [ %s ]' % ( self.name, ', '.join(self.values) ) )

		Option.__set__( self, obj, value )

	@property
	def type( self ):
		return str

class ComponentConfigurationCreator( type ):
	def __call__( cls ):
		options = {}

		for name, value in inspect.getmembers( cls, inspect.isdatadescriptor ):
			if not name.startswith("__"):
				value.__name__ = name
				options[ name ] = value

		instance = type.__call__( cls )
		instance.options = options
		return instance

class ComponentConfiguration( object ):
	__metaclass__ = ComponentConfigurationCreator

class Configurator( object ):
	"""
	Class handling components and their configuration.
	"""

	def __init__( self ):
		"""
		Initialize object of this class
		"""

		self.configurations	= {}
		self.options		= {}
	
	def registerComponent( self, component, configuration ):
		"""
		Registers a component in L{Configurator}.
		"""
		if component in self.configurations:
			raise ConfigurationError( "Component %s already registered!" % component )

		self.configurations[ component ] = configuration

		for name, option in configuration.options.iteritems():
			if name in self.options:
				raise ConfigurationError( "Option %s in component %s cannot be registered: conflict with %s component!" % (component, name, self.options[ name ]) )
			self.options[ name ] = ( option, configuration )

class CLIHelpFormatter( optparse.IndentedHelpFormatter ):
	"""
	Help formatter.

	@ivar textwrapper: stores L{TextWrapper} instance, which is used to format message
	@type textwrapper: L{TextWrapper}
	"""

	def __init__( self, **kwargs ):
		"""
		Initializing object of this class
		"""
		optparse.IndentedHelpFormatter.__init__( self, **kwargs )

		self.textwrapper = textwrap.TextWrapper()
		self.textwrapper.initial_indent = ' ' * 6
		self.textwrapper.subsequent_indent = ' ' * 6
		self.textwrapper.width = 80

	def format_usage( self, usage ):
		"""
		Prepare string formatted to show usage.

		@param usage: usage to show
		@return: string with formatted usage
		"""

		return  "\033[33mUsage: %s\033[0m\n" % usage
	
	def format_heading( self, heading ):
		"""
		Prepare string formatted to show heading.

		@param heading: heading to show
		@return: string with formatted heading
		"""

		return  "\033[33m%s:\033[0m\n" % heading
	
	def format_option( self, option ):
		"""
		Prepare string formatted to show option.

		@param option: option to show
		@return: string with formatted option
		"""

		if option.metavar:
			metavar = ' %s' % option.metavar
		else:
			metavar = ''

		options = []
		
		for short in option._short_opts:
			options.append( '%s%s' % ( short, metavar ) )

		for long in option._long_opts:
			options.append( '%s%s' % ( long, metavar ) )
		
		options = '  \033[1m%s\033[0m' % ', '.join( options )
		help	= '\n'.join( self.textwrapper.wrap( option.help ) )

		if option.default and option.default != ('NO','DEFAULT'):
			default	= ' (\033[36mdefault value: %s\033[0m)' % str( option.default )
		else:
			default = ''

		return '%s%s\n%s\n\n' % ( options, default, help )

class CLIConfigurator( Configurator ):
	"""
	Configurator that reads configuration from command line interface.
	"""

	def __init__( self, description ):
		"""
		L{CLIConfigurator} constructor.

		@param description: the program description, which will be shown in CLI
		@type description: L{str}
		"""

		Configurator.__init__( self )

		self.__description = description

	def configParse( self ):
		"""
		Parses command line and extracts configuration from it.
		"""

		parser = optparse.OptionParser()
		parser.formatter = CLIHelpFormatter()
		parser.description = self.__description

		self.__parser = parser

		def ErrorMethodReplacement( msg ):
			raise ConfigurationError( msg )

		self.__parser.error = ErrorMethodReplacement

		for name in sorted( self.options ):
			option = self.options[ name ][0]

			if option.short is not None:
				short = '-' + option.short
			else:
				short = ''

			long = '--' + option.__name__.replace('_','-')

			ext = dict( dest=option.__name__, help=option.help )

			if option.arg_name is not None:
				ext['metavar'] = option.arg_name

			try:
				if option.type is str:
					ext['type'] = 'string'
				elif option.type is int:
					ext['type'] = 'int'
				elif option.type is float:
					ext['type'] = 'float'
				ext['action'] = 'store'
			except AttributeError:
				if option.default is True:
					ext['action']  = 'store_false'
					ext['default'] = True
				else:
					ext['action']  = 'store_true'
					ext['default'] = False

			try:
				ext['default'] = option.default
			except AttributeError:
				pass

			parser.add_option( short, long, **ext )

		values, args = parser.parse_args( )

		for name in sorted( self.options ):
			value = values.__dict__[ name ]

			setattr( self.options[ name ][1], name, value )

	def configCommit( self, component = None ):
		"""
		Commits configuration to provided component.

		If no component is provided it commits configuration to all components.

		@param component: configurable component
		@type component: L{object} or L{type} or L{None}
		"""

		if component:
			component.configure( self.configurations[ component ] )
		else:
			for component, configuration in self.configurations.iteritems():
				component.configure( configuration )
	
	def help( self ):
		"""
		Shows help message.
		"""

		self.__parser.print_help()

from tp.server.logging import Logger

class LoggerConfiguration( ComponentConfiguration ):
	component		= Logger

	log_level		= StringSetOption( short='l', default='info', values=set( Logger.levels ),
							help='All log message with level lower than provided will be dropped. Allowed log levels are: %s.' %
							', '.join( sorted(Logger.levels, lambda x,y: cmp(Logger.levels[x], Logger.levels[y])) ), arg_name='LEVEL' )
	log_drop_time	= BooleanOption( default=False,
							help='Force logger to drop time prefix for each printed log message.' )
	log_drop_system	= BooleanOption( default=False,
							help='Force logger to drop component name (where the message was generated) prefix from each printed log message.' )

from tp.server.server import ThousandParsecServerFactory

class ThousandParsecServerConfiguration( ComponentConfiguration ):
	component	= ThousandParsecServerFactory

	tcp_port	= IntegerOption( short='p', default=6923, min=1, max=65535,
						help='Specifies number of listening port.', arg_name='PORT' )
	tls_port	= IntegerOption( default=6924, min=1, max=65535,
						help='Specifies number of TLS listening port.', arg_name='PORT' )
	listen_tls	= BooleanOption( short='t', default=False,
						help='Turns on TLS listener.' )

from tp.server.model import DatabaseManager

class DatabaseConfiguration( ComponentConfiguration ):
	component = DatabaseManager

	database = StringOption( short='D', default='sqlite:///tp.db', 
							help='Database engine supported by SQLAlchemy.', arg_name='DATABASE' )


__all__ = [ 'ConfigurationError', 'ConfigurationOption',
			'ComponentConfiguration', 'CLIConfigurator', 'Configurator',
			'BooleanOption', 'IntegerOption', 'StringOption',
			'StringSetOption', 'LoggerConfiguration',
			'ThousandParsecServerConfiguration', 'DatabaseConfiguration' ]
