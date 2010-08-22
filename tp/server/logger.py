#!/usr/bin/env python

import logging, string, linecache, sys, inspect

class Formatter( logging.Formatter ):
	colors = {
			'gry0': '\033[0;30m',
			'gry1': '\033[1;30m',
			'red0': '\033[0;31m',
			'red1': '\033[1;31m',
			'grn0': '\033[0;32m',
			'grn1': '\033[1;32m',
			'yel0': '\033[0;33m',
			'yel1': '\033[1;33m',
			'blu0': '\033[0;34m',
			'blu1': '\033[1;34m',
			'mgt0': '\033[0;35m',
			'mgt1': '\033[1;35m',
			'cyn0': '\033[0;36m',
			'cyn1': '\033[1;36m',
			'wht0': '\033[0;37m',
			'wht1': '\033[1;37m',
			'coff': '\033[0m' }

	levelcolors = {
			'CRITICAL' : '${red1}',
			'ERROR'    : '${red1}',
			'WARNING'  : '${yel1}',
			'INFO'     : '${coff}',
			'DEBUG'    : '${wht0}' }


	prefixes = [ path for path in sys.path if len(path) ]

	@staticmethod
	def colorizeMessage( msg ):
		return string.Template( msg ).safe_substitute( Formatter.colors )

	@staticmethod
	def cutFilenamePrefix( prefixes, filename ):
		matchingPrefixes = [ prefix for prefix in prefixes if filename.startswith( prefix ) ]

		return filename.split('%s/' % max( matchingPrefixes ), 1)[1] if matchingPrefixes else filename

	def fetchFrames( self, tb ):
		frames = []

		while tb:
			frame = tb.tb_frame
			code  = tb.tb_frame.f_code

			frames.append( (code.co_name, code.co_filename, frame.f_lineno, frame.f_locals, frame.f_globals) )

			tb = tb.tb_next

		return frames

	def formatException( self, ex ):
		frames = self.fetchFrames( ex[2] )

		s = [ '${wht1}---- Begin of failure %s ----${coff}' % ex[0].__name__ ]

		for method, filename, lineno, localVars, globalVars in frames:
			s.append(' ${wht1}in %s: %s(...)${coff}' % (self.cutFilenamePrefix( self.prefixes, filename ), method))

			lines = [ linecache.getline(filename, n).rstrip() for n in range( lineno-1, lineno+2 ) ]

			s.append(' %d: %s' % (lineno-1, lines[0]))
			s.append(' %d: ${yel1}%s${coff}' % (lineno, lines[1]))
			s.append(' %d: %s' % (lineno+1, lines[2]))
			s.append('')

			for name, val in localVars.iteritems():
				s.append(' %s : %s' % (name, repr(val)))

			s.append('')

		s.append( '${wht1}---- End of failure %s ----${coff}' % ex[0].__name__ )

		return s

	def format( self, record ):
		if string.find(self._fmt,'%(asctime)') >= 0:
			record.asctime = self.formatTime( record, self.datefmt )

		caller = logging.root.findCaller()

		for frame, filename, lineno, function, code_context, index in inspect.getouterframes( inspect.currentframe() ):
			if (filename, lineno, function) == caller:
				try:
					name = frame.f_locals['self'].__class__.__name__
				except (KeyError, AttributeError):
					name = frame.f_globals['__name__'].split('.')[-1]

		if record.name != logging.root.name:
			if record.name.startswith('sqlalchemy'):
				logger_name = 'SQLAlchemy'
			elif record.name.startswith('twisted'):
				logger_name = 'Twisted'
			else:
				logger_name = record.name

			record.name = '.'.join([logger_name, name])
		else:
			record.name = name

		s = []

		for line in record.getMessage().splitlines():
			record.message = ''.join( [ self.levelcolors[ record.levelname ], line, '${coff}' ] )
			s.append( self._fmt % record.__dict__ )

		if record.exc_info:
			if not record.exc_text:
				record.exc_text = self.formatException( record.exc_info )

		if record.exc_text:
			for line in record.exc_text:
				record.message = line
				s.append( self._fmt % record.__dict__ )

		return Formatter.colorizeMessage( '\n'.join(s) )

__all__ = [ 'logger', 'Formatter' ]
