import collections

from clientsession import ClientSessionHandler
from client import ThousandParsecClientFactory
from test import TestCase

from tp.server.packet import PacketFactory, PacketFormatter
from tp.server.logging import logctx, msg

def ichain( *args ):#{{{
	for a in args:
		try:
			r = None
			while True:
				r = yield a.send(r)
		except StopIteration:
			pass
#}}}

class IncrementingSequenceMixin( object ):#{{{
	@property
	def seq( self ):
		try:
			self.__seq += 1
		except AttributeError:
			self.__seq = 1
		
		return self.__seq
#}}}

class Expect( collections.Container ):#{{{
	def __init__( self, *packets ):
		self.packets = packets
	
	def __contains__( self, request ):
		for packet in self.packets:
			# case: packet is packet type
			if not isinstance( packet, tuple ) and request.type == packet:
				return True

			if isinstance( packet, tuple ):
				# case: p is ('Fail', code) 
				try:
					packet_type, packet_code = packet
				except ValueError:
					pass
				else:
					if request.type == packet_type:
						request_code = request._structures[0].as_string(request, request.__class__)

						if request_code == packet_code:
							return True

				try:
					sequence, packet_num, packet_type = packet
				except ValueError:
					pass
				else:
					if isinstance( request, list ) and len(request) == packet_num + 1 and request[0].type == 'Sequence':
						if all( r.type == packet_type for r in request[1:] ):
							return True

		return False

	def __str__( self ):
		s = []

		for packet in self.packets:
			if isinstance( packet, tuple ):
				if len( packet ) == 2:
					s.append( "%s with code %s" % packet )
				elif len( packet ) == 3:
					s.append( "%s of %d %s packets" % packet )
			else:
				s.append( packet )

		return ", ".join( s )
#}}}

class TestSession( TestCase, ClientSessionHandler ):#{{{
	NoFailAllowed = True

	def __init__( self ):
		super( TestSession, self ).__init__()

		self.bundle = []
		self.count  = 0
		self.protocol = PacketFactory()["TP03"]
		self.scenarioList = []
		self.request = None
	
	def setUp( self ):
		msg( "${wht1}Setting up %s test...${coff}" % self.__class__.__name__, level='info' ) 

		ThousandParsecClientFactory().makeTestSession( self )
	
	def tearDown( self ):
		msg( "${wht1}Tearing down %s test...${coff}" % self.__class__.__name__, level='info' ) 

	def run( self ):
		msg( "${wht1}Starting %s test...${coff}" % self.__class__.__name__, level='info' ) 
	
	@logctx
	def sessionStarted( self, transport ):
		super( TestSession, self ).sessionStarted( transport )

		msg( "Connection established.", level="info" )

		self.scenarioList.append( self.__iter__() )

		self.scenario = ichain( *self.scenarioList )
		self.step()

	@logctx
	def packetReceived( self, packet ):
		packet.type = packet.__class__.__name__

		msg( "Received ${cyn1}%s${coff} packet." % packet.type, level="info" )

		if self.NoFailAllowed and packet.type == "Fail":
			self.failed( packet, "Fail packet received!" )
		elif packet.type == "Sequence":
			self.count = packet.number
			self.bundle.append( packet )
		elif self.count > 0:
			self.bundle.append( packet )
			self.count -= 1

			if self.count == 0:
				bundle = self.bundle
				self.bundle = []

				if self.expected and bundle not in self.expected:
					self.failed( bundle, "Received unexpected packets %s!" % ", ".join( p.type for p in bundle ) )
				else:
					self.step( bundle )
		elif self.expected and packet not in self.expected:
			self.failed( packet, "Received unexpected packet %s!" % packet.type )
		else:
			self.step( packet )

	def step( self, response = None ):
		try:
			instruction = self.scenario.send( response )
		except StopIteration, ex:
			self.succeeded()
		else:
			if isinstance( instruction, tuple ):
				request, self.expected = instruction
			else:
				request, self.expected = instruction, None

			self.transport.sendPacket( request )

			self.request = request
			self.request.type = request.__class__.__name__

			if request is not None:
				msg( "Sending ${cyn1}%s${coff} packet." % request._name, level="info" )
			
			if isinstance( self.expected, Expect ):
				msg( "${mgt1}Expecting response of type ${wht1}%s${mgt1}.${coff}" % self.expected, level="info" )
	
	def succeeded( self ):
		msg( "${grn1}Test %s succeeded!${coff}" % self.__class__.__name__, level='notice' ) 

		self.transport.loseConnection()
		
		super( TestSession, self ).succeeded()

	def failed( self, response, reason ):
		msg( "${red1}----=[ ERROR REPORT START ]=-----${coff}", level='error' )
		msg( "${red1}Failed test name:${coff}\n %s" % self.__class__.__name__, level='error' ) 
		msg( "${red1}Description:${coff}\n %s" % self.__doc__.strip(), level='error' ) 
		msg( "${red1}Reason:${coff}\n %s" % reason, level='error' ) 

		if self.request:
			msg( "${red1}Failing request %s:${coff}" % self.request.type, level='error' )
			msg( PacketFormatter( self.request ), level='error' )

		if response:
			if isinstance( response, list ):
				msg( "${red1}Wrong response %s:${coff}" % ", ".join( r.type for r in response ), level='error' )
				for r in response:
					msg( PacketFormatter( r ), level='error' )
			else:
				msg( "${red1}Wrong response %s:${coff}" % response.type, level='error' )
				msg( PacketFormatter( response ), level='error' )

		if self.expected:
			msg( "${red1}Expected:${coff}\n %s" % self.expected, level='error' ) 

		msg( "${red1}-----=[ ERROR REPORT END ]=------${coff}", level='error' )

		self.transport.loseConnection()

		super( TestSession, self ).failed( reason )
#}}}

class ConnectedTestSession( TestSession, IncrementingSequenceMixin ):#{{{
	def __init__( self ):
		super( ConnectedTestSession, self ).__init__()

		self.scenarioList.append( self.__connect() )

	def __connect( self ):
		Connect = self.protocol.use( 'Connect' )

		yield Connect( self.seq, "tpserver-tests client" ), Expect( 'Okay' )
#}}}

class AuthorizedTestSession( TestSession, IncrementingSequenceMixin ):#{{{
	Game		= "tp"
	Login		= "test"
	Password	= "test"

	def __init__( self ):
		super( AuthorizedTestSession, self ).__init__()

		self.scenarioList.append( self.__login() )

	def __login( self ):
		Connect, Login = self.protocol.use( 'Connect', 'Login' )

		yield Connect( self.seq, "tpserver-tests client" ), Expect( 'Okay' )
		yield Login( self.seq, "%s@%s" % ( self.Login, self.Game), self.Password ), Expect( 'Okay' )
#}}}

__all__ = [ 'IncrementingSequenceMixin', 'Expect', 'TestSession', 'ConnectedTestSession', 'AuthorizedTestSession' ]
