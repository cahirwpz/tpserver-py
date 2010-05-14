#!/usr/bin/env python

import string, sys, linecache

from twisted.python import log, util, context, failure

msg = log.msg
err = log.err

def cut_filename_prefix( prefixes, filename ):#{{{
	"""
	Cuts prefix from filename
	@param prefixes: list of possible prefixes to cut
	@param filename: filename to cut prefix from
	@return: filename without prefix
	"""
	matchingPrefixes = [ prefix for prefix in prefixes if filename.startswith( prefix ) ]

	return filename.split('%s/' % max( matchingPrefixes ), 1)[1] if matchingPrefixes else filename
#}}}

def format_frames(frames, write, detail="default"):#{{{
	"""
	Formating function uses L{cut_filename_prefix} to get filename
	@param frames: frames to format
	@param write: method used to show formatted frames
	@param detail: not used
	"""
	level = globals()["CurrentLogLevel"]
	w = write

	prefixes = [ path for path in sys.path if len(path) ]

	if level >= 2:
		for method, filename, lineno, localVars, globalVars in frames:
			w( ' ${wht1}in %s: %d: %s(...)${coff}\n' % (cut_filename_prefix( prefixes, filename ), lineno, method))
	else:
		for method, filename, lineno, localVars, globalVars in frames:
			w( ' ${wht1}in %s: %s(...)${coff}\n' % (cut_filename_prefix( prefixes, filename ), method))

			lines = [ linecache.getline(filename, n).rstrip() for n in range( lineno-1, lineno+2 ) ]

			w( '  %d: %s\n' % (lineno-1, lines[0] ) )
			w( '  %d: ${yel1}%s${coff}\n' % (lineno, lines[1] ) )
			w( '  %d: %s\n' % (lineno+1, lines[2] ) )
			w( '  \n' )
			for name, val in localVars:
				w( '  %s : %s\n' %  (name, repr(val)))
			w( '  \n' )
#}}}

failure.format_frames = format_frames
failure.EXCEPTION_CAUGHT_HERE = "*** exception caught here ***"

def logctx( fun ):#{{{
	def wrapper( self, *args, **kwargs ):
		return log.callWithLogger( self, fun, self, *args, **kwargs )
	return wrapper
#}}}

class Logger( log.FileLogObserver ):#{{{
	"""
	Logger class

	@cvar colors: colors of logging messages
	@type colors: dict
	@cvar levels: levels of logging information output
	@type levels: dict
	@ivar __level: current cog level
	"""

	colors =  {	'gry0':	'\033[0;30m',
				'gry1':	'\033[1;30m',
				'red0':	'\033[0;31m',
				'red1':	'\033[1;31m',
				'grn0':	'\033[0;32m',
				'grn1':	'\033[1;32m',
				'yel0':	'\033[0;33m',
				'yel1':	'\033[1;33m',
				'blu0':	'\033[0;34m',
				'blu1':	'\033[1;34m',
				'mgt0':	'\033[0;35m',
				'mgt1':	'\033[1;35m',
				'cyn0':	'\033[0;36m',
				'cyn1':	'\033[1;36m',
				'wht0':	'\033[0;37m',
				'wht1':	'\033[1;37m',
				'coff':	'\033[0m' }


	levels =  {	'debug2'	:	0, 		# Verbose debug information
				'debug1'	:	1, 		# Normal debug information
				'info'		:	2, 		# Informational messages
				'notice'	:	3, 		# Conditions that are not error conditions, but that may require special
										# handling. (preferable	colors: wht0 / cyn0)
				'warning'	:	4, 		# Warning messages. (prefferable colors: yel1)
				'error'		:	5, 		# Error messages. (prefferable colors: red1)
				'critical'	:	6 		# Critical messages. Most probably they will be accompanied with program 
										# termination. (prefferable colors: red1)
			  }
	
	@staticmethod
	def colorizeMessage( msg ):
		"""
		Method to colorize messages
		@return: colorized message
		"""
		return string.Template( msg ).safe_substitute( Logger.colors )

	def __init__( self, level = 'debug1' ):
		"""
		Constructor
		"""
		log.FileLogObserver.__init__( self, sys.stderr )

		self.__level = level

		globals()["CurrentLogLevel"] = Logger.levels[ self.__level ]

	@staticmethod
	def updateContext( logger ):
		ctx = context.get(log.ILogContext)

		ctx.update( { 'system': logger.logPrefix() } )

	def emit( self, eventDict ):
		try:
			level = eventDict[ 'level' ]
		except KeyError:
			level = 'info'

		try:
			_failure = eventDict[ 'failure' ]

			message = [ '${wht1}---- Begin of failure %s ----${coff}\n' % _failure.type.__name__ ]

			for line in _failure.getTraceback(elideFrameworkCode=1).splitlines():
				message.append( line )

			message.append( '${wht1}---- End of failure %s ----${coff}\n' % _failure.type.__name__ )

			eventDict[ 'message' ]	= message
			eventDict[ 'system' ]	= Logger.colorizeMessage( "${red1}%s$coff" % eventDict[ 'system' ] )
			eventDict[ 'isError' ]	= 0

			level = 'error'
		except KeyError:
			pass

		if Logger.levels[ level ] >= Logger.levels[ self.__level ]:
			format = dict( time='', system='' )

			format['time'] = '%s ' % self.formatTime( eventDict[ 'time' ] )
			format['system'] = '[%s] ' % eventDict[ 'system' ]

			for text in eventDict[ 'message' ]:
				if text is None or eventDict[ 'system' ] == '-':
					return

				if type( text ) <= unicode:
					text = text.splitlines()

				for line in text:
					format['text'] = Logger.colorizeMessage( line )

					util.untilConcludes( self.write, log._safeFormat( '%(time)s%(system)s%(text)s\n', format ) )

			util.untilConcludes( self.flush )
#}}}

__all__ = [ 'Logger', 'logctx', 'log', 'err' ]
