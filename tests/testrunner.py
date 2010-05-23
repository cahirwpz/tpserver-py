from twisted.internet import reactor, ssl
from OpenSSL import SSL

from tp.server.configuration import ComponentConfiguration, StringOption, IntegerOption, BooleanOption
from tp.server.logging import msg, logctx
from tp.server.protocol import ThousandParsecProtocol
from tp.server.packet import PacketFactory, PacketFormatter

from client import ThousandParsecClientFactory

from testcases import __testcases__

class ClientTLSContext( ssl.ClientContextFactory ):
	method = SSL.TLSv1_METHOD

class TestRunner( object ):#{{{
	def __init__( self ):
		self.__protocol = PacketFactory().objects
		self.__factory = ThousandParsecClientFactory()
		self.tests = list( __testcases__ )

		#self.__manager = TestManager()
		#self.__chooser = TestSelector( self.__manager )

	@logctx
	def __continue( self ):
		try:
			test = self.tests.pop(0)
		except IndexError, ex:
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
			msg( "${red1}Description:${coff}\n %s" % test.description, level='error' ) 
			msg( "${red1}Reason:${coff}\n %s" % test.reason, level='error' ) 
			if test.failRequest:
				msg( "${red1}Failing request %s:${coff}" % test.failRequest._name, level='error' )
				msg( PacketFormatter( test.failRequest ), level='error' )
			if test.failResponse:
				msg( "${red1}Wrong response %s:${coff}" % test.failResponse._name, level='error' )
				msg( PacketFormatter( test.failResponse ), level='error' )
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

__all__ = [ 'TestRunner', 'TestRunnerConfiguration' ]
