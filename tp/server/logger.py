#!/usr/bin/env python

import logging, string, linecache, sys

def logctx( fun ):
	def wrapper( self, *args, **kwargs ):
		old_name = logging.root.name
		
		logging.root.name = self.logPrefix()

		value = fun( self, *args, **kwargs )

		logging.root.name = old_name
	
		return value

	return wrapper 

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
			'INFO'     : '${wht1}',
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
		if record.name.startswith('sqlalchemy'):
			record.name = 'SQLAlchemy'

		if string.find(self._fmt,"%(asctime)") >= 0:
			record.asctime = self.formatTime( record, self.datefmt )

		record.color   = self.levelcolors[ record.levelname ]
		record.nocolor = '${coff}'

		s = []

		for line in record.getMessage().splitlines():
			record.message = line
			s.append( self._fmt % record.__dict__ )

		if record.exc_info:
			if not record.exc_text:
				record.exc_text = self.formatException( record.exc_info )

		if record.exc_text:
			for line in record.exc_text:
				record.message = line
				s.append( self._fmt % record.__dict__ )

		return Formatter.colorizeMessage( "\n".join(s) )

__all__ = [ 'logger', 'Formatter' ]
