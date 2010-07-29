#!/usr/bin/env python

import fnmatch
from collections import Iterator

from twisted.internet import reactor, ssl
from OpenSSL import SSL

from tp.server.configuration import ComponentConfiguration, StringOption, IntegerOption, BooleanOption, ConfigurationError
from tp.server.logging import Logger, msg, logctx
from tp.server.protocol import ThousandParsecProtocol
from tp.server.packet import PacketFactory, PacketFormatter

from client import ThousandParsecClientFactory

from testcases import __manager__

class ClientTLSContext( ssl.ClientContextFactory ):
	method = SSL.TLSv1_METHOD

class TestSelector( Iterator ):#{{{
	def __init__( self ):
		self.__manager	= __manager__
		self.__tests	= []
		self.__index	= 0
	
	def next( self ):
		if self.__index >= len( self.__tests ):
			raise StopIteration

		name = self.__tests[ self.__index ]

		self.__index += 1

		return self.__manager[ name ]

	def configure( self, configuration ):
		tests = configuration.tests

		if tests == 'LIST':
			raise SystemExit( Logger.colorizeMessage( '\n'.join( self.__manager.getReport() ) ) )
		elif tests == 'DEFAULT':
			self.__tests = [ 'DEFAULT' ]
		elif tests == 'ALL':
			self.__tests = self.__manager.keys()
		else:
			for name in tests.split(','):
				try:
					names = fnmatch.filter( self.__manager.keys(), name )

					if not names:
						raise KeyError( 'No test matching \'%s\'' % name )

					self.__tests.extend( names )
				except KeyError, ex:
					raise SystemExit( ex )

		if not self.__tests:
			raise ConfigurationError( 'test run is empty' )

#}}}

class TestSelectorConfiguration( ComponentConfiguration ):#{{{
	tests = StringOption( short='t', default='ALL',
						  help='Specifies which tests will be added to test run. TEST-LIST is a list of test names or glob (see unix manual pages) patterns separated by comma. There are some arguments to this option that have a special meaning. \'LIST\' will force to display all available tests and finish the application. \'ALL\' will add all available test to test run.', arg_name='TEST-LIST' )
#}}}

__all__ = [ 'TestSelector', 'TestSelectorConfiguration', 'TestManager' ]

class TestRunner( object ):#{{{
	def __init__( self, selector ):
		self.__protocol	= PacketFactory()["TP03"]
		self.__factory	= ThousandParsecClientFactory()
		self.__selector	= selector

	@logctx
	def __continue( self ):
		try:
			test = self.__selector.next()
		except StopIteration, ex:
			reactor.stop()
		else:
			test.finished = self.__finished

			ThousandParsecProtocol.SessionHandlerType = test

			msg( "${wht1}Starting %s test...${coff}" % test.__name__, level='info' ) 

			if self.__use_tls:
				reactor.connectSSL( self.__hostname, self.__tls_port_num, self.__factory, ssl.ClientContextFactory() )
			else:
				reactor.connectTCP( self.__hostname, self.__tcp_port_num, self.__factory )

	@logctx
	def __finished( self, test ):
		if test.status == True:
			msg( "${grn1}Test %s succeeded!${coff}" % test.__class__.__name__, level='notice' ) 
		else:
			msg( "${red1}----=[ ERROR REPORT START ]=-----${coff}", level='error' )
			msg( "${red1}Failed test name:${coff}\n %s" % test.__class__.__name__, level='error' ) 
			msg( "${red1}Description:${coff}\n %s" % test.__doc__.strip(), level='error' ) 
			msg( "${red1}Reason:${coff}\n %s" % test.reason, level='error' ) 

			if test.failRequest:
				msg( "${red1}Failing request %s:${coff}" % test.failRequest.type, level='error' )
				msg( PacketFormatter( test.failRequest ), level='error' )

			if test.failResponse:
				if isinstance( test.failResponse, list ):
					msg( "${red1}Wrong response %s:${coff}" % ", ".join( r.type for r in test.failResponse ), level='error' )
					for r in test.failResponse:
						msg( PacketFormatter( r ), level='error' )
				else:
					msg( "${red1}Wrong response %s:${coff}" % test.failResponse.type, level='error' )
					msg( PacketFormatter( test.failResponse ), level='error' )

			if test.expected:
				msg( "${red1}Expected:${coff}\n %s" % test.expected, level='error' ) 

			msg( "${red1}-----=[ ERROR REPORT END ]=------${coff}", level='error' )

		self.__continue()

	def configure( self, configuration ):
		self.__hostname = configuration.hostname
		self.__tcp_port_num = configuration.tcp_port
		self.__tls_port_num = configuration.tls_port
		self.__use_tls = configuration.use_tls

	def start( self ):
		reactor.callLater( 0, self.__continue )
	
	def logPrefix( self ):
		return self.__class__.__name__
#}}}

class TestRunnerConfiguration( ComponentConfiguration ):#{{{
	component = TestRunner

	hostname	= StringOption( short='H', default='localhost',
								help='Specifies server hostname.', arg_name='FQDN' )
	tcp_port	= IntegerOption( short='p', default=6923, min=1, max=65535,
								help='Specifies server port.', arg_name='PORT' )
	tls_port	= IntegerOption( default=6924, min=1, max=65535,
								help='Specifies TLS server port.', arg_name='PORT' )
	use_tls		= BooleanOption( short='T', default=False,
								help='Use TLS instead of TCP connection.' )
#}}}

__all__ = [ 'TestRunner', 'TestRunnerConfiguration', 'TestSelector', 'TestSelectorConfiguration' ]
