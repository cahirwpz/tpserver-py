import time

from clientsession import ClientSessionHandler
from client import ThousandParsecClientFactory
from test import TestCase

from tp.server.packet import PacketFactory, PacketFormatter
from tp.server.logging import logctx, msg, err

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

class Expect( object ):#{{{
	def __init__( self, packet ):
		assert isinstance( packet, str )

		self.__packet = packet

	def __eq__( self, response ):
		return response.type == self.__packet

	def __ne__( self, response ):
		return not (self == response)

	def __str__( self ):
		return self.__packet
#}}}

class ExpectFail( Expect ):#{{{
	def __init__( self, *codes ):
		Expect.__init__( self, 'Fail' )

		self.__codes = set( codes )

	def __eq__( self, response ):
		if Expect.__eq__( self, response ):
			response_code = response._structures[0].as_string( response, response.__class__ )

			if response_code in self.__codes:
				return True

		return False

	def __str__( self ):
		return "Fail with code%s %s" % (
				"s" if len( self.__codes ) > 1 else "",
				" or ".join( self.__codes ) )
#}}}

class ExpectSequence( Expect ):#{{{
	def __init__( self, *packets ):
		Expect.__init__( self, 'Sequence' )

		if isinstance( packets[0], int ) and len( packets ) == 2:
			if isinstance( packets[1], str ):
				packet = Expect( packets[1] )
			else:
				packet = packets[1]

			self.__packets = [ packet for i in range(packets[0]) ]
		else:
			self.__packets = []

			for packet in packets:
				if isinstance( packet, Expect ):
					self.__packets.append( packet )
				elif isinstance( packet, str ):
					self.__packets.append( Expect( packet ) )
				else:
					raise TypeError( 'Wrong choice type!' )

	def __eq__( self, response ):
		if not isinstance( response, list ):
			return False

		if not Expect.__eq__( self, response[0] ):
			return False

		if len( response ) != len( self.__packets ) + 1:
			return False
		
		if any( packet != choice for packet, choice in zip( response[1:], self.__packets ) ):
			return False

		return True
	
	def __str__( self ):
		return "Sequence of (%s) packets" % ( ", ".join( str(packet) for packet in self.__packets ) )
#}}}

class ExpectOneOf( Expect ):#{{{
	def __init__( self, *choices ):
		self.__choices = []

		for choice in choices:
			if isinstance( choice, Expect ):
				self.__choices.append( choice )
			elif isinstance( choice, str ):
				self.__choices.append( Expect( choice ) )
			else:
				raise TypeError( 'Wrong choice type!' )

	def __eq__( self, response ):
		return any( response == choice for choice in self.__choices )

	def __str__( self ):
		return ", ".join( str( choice ) for choice in self.__choices )
#}}}

class TestSessionUtils( object ):#{{{
	def datetimeToInt( self, t ):
		return long( time.mktime( time.strptime( t.ctime() ) ) )
#}}}

class TestSession( TestCase, ClientSessionHandler ):#{{{
	def __init__( self, **kwargs ):
		super( TestSession, self ).__init__( **kwargs )

		self.bundle		= []
		self.count 		= 0
		self.protocol	= PacketFactory()["TP03"]
		self.scenarioList = []

		self.request	= None
		self.response	= None
		self.expected	= None

		self.__finished = False
	
	def setUp( self ):
		msg( "${wht1}Setting up %s test...${coff}" % self.__class__.__name__, level='info' ) 

		ThousandParsecClientFactory().makeTestSession( self )
	
	def tearDown( self ):
		msg( "${wht1}Tearing down %s test...${coff}" % self.__class__.__name__, level='info' ) 

		self.transport.loseConnection()

	def run( self ):
		msg( "${wht1}Starting %s test...${coff}" % self.__class__.__name__, level='info' ) 
	
	@logctx
	def sessionStarted( self, transport ):
		super( TestSession, self ).sessionStarted( transport )

		msg( "Connection established.", level="info" )

		if hasattr( self, '__iter__' ):
			self.scenarioList.append( self.__iter__() )

		self.scenario = ichain( *self.scenarioList )

		self.step()

	@logctx
	def packetReceived( self, packet ):
		packet.type = packet.__class__.__name__

		msg( "Received ${cyn1}%s${coff} packet." % packet.type, level="info" )

		if self.expected is None and packet.type == "Fail":
			self.response = packet
			self.failed( "Fail packet received!" )
		elif packet.type == "Sequence":
			self.count = packet.number
			self.bundle.append( packet )
		elif self.count > 0:
			self.bundle.append( packet )
			self.count -= 1

			if self.count == 0:
				bundle = self.bundle
				self.bundle = []

				if self.expected and self.expected != bundle:
					self.response = bundle
					self.failed( "Received unexpected packets %s!" % ", ".join( p.type for p in bundle ) )
				else:
					self.step( bundle )
		elif self.expected and self.expected != packet:
			self.response = packet
			self.failed( "Received unexpected packet %s!" % packet.type )
		else:
			self.expected = None
			self.response = packet
			self.step( packet )

	def step( self, response = None ):
		if not self.__finished:
			try:
				instruction = self.scenario.send( response )
			except StopIteration, ex:
				self.succeeded()
			except AssertionError, ex:
				self.failed( str(ex) )
			except Exception, ex:
				err()
				self.failed( "Scenario failed with unexpected error: %s: %s" % (ex.__class__.__name__, str(ex)) )
			else:
				if isinstance( instruction, tuple ):
					request, self.expected = instruction
					assert isinstance( self.expected, Expect ), "Second value given to yield must be Expect class instance!"
				else:
					request, self.expected = instruction, None
					msg( "${yel1}Yielding a single value (without Expect instance) within a scenario is discouraged!${coff}", level="warning" )

				self.transport.sendPacket( request )

				self.request = request
				self.request.type = request.__class__.__name__

				if request is not None:
					msg( "Sending ${cyn1}%s${coff} packet." % request._name, level="info" )
				
				if isinstance( self.expected, Expect ):
					msg( "${mgt1}Expecting response of type ${wht1}%s${mgt1}.${coff}" % self.expected, level="info" )

	def failed( self, reason ):
		if not self.__finished:
			self.__finished = True

			super( TestSession, self ).failed( reason )

	def succeeded( self ):
		if not self.__finished:
			self.__finished = True

			super( TestSession, self ).succeeded()
	
	def report( self ):
		if self.status:
			TestCase.report( self )
		else:
			TestCase.report( self, 'prologue' )

			if self.request:
				msg( "${red1}Failing request %s:${coff}" % self.request.type, level='error' )
				msg( PacketFormatter( self.request ), level='error' )

			if self.response:
				if isinstance( self.response, list ):
					msg( "${red1}Wrong response %s:${coff}" % ", ".join( r.type for r in self.response ), level='error' )
					for r in self.response:
						msg( "${wht1}Packet:${coff}", level='error' )
						msg( PacketFormatter( r ), level='error' )
				else:
					msg( "${red1}Wrong response %s:${coff}" % self.response.type, level='error' )
					msg( PacketFormatter( self.response ), level='error' )

			if self.expected:
				msg( "${red1}Expected:${coff}\n %s" % self.expected, level='error' ) 

			TestCase.report( self, 'epilogue' )
#}}}

class ConnectedTestSession( TestSession, IncrementingSequenceMixin ):#{{{
	def __init__( self, **kwargs ):
		super( ConnectedTestSession, self ).__init__( **kwargs )

		self.scenarioList.append( self.__connect() )

	def __connect( self ):
		Connect = self.protocol.use( 'Connect' )

		yield Connect( self.seq, "tpserver-tests client" ), Expect( 'Okay' )
#}}}

class AuthorizedTestSession( TestSession, IncrementingSequenceMixin ):#{{{
	def __init__( self, **kwargs ):
		super( AuthorizedTestSession, self ).__init__( **kwargs )

		self.scenarioList.append( self.__login() )
	
	@property
	def game( self ):
		return self.ctx['game']

	@property
	def player( self ):
		return self.ctx['players'][0]

	def __login( self ):
		Connect, Login = self.protocol.use( 'Connect', 'Login' )

		yield Connect( self.seq, "tpserver-tests client" ), Expect( 'Okay' )
		yield Login( self.seq, "%s@%s" % ( self.player.username, self.game.name ), self.player.password ), Expect( 'Okay' )
#}}}

__all__ = [ 'IncrementingSequenceMixin', 'Expect', 'ExpectFail',
			'ExpectSequence', 'ExpectOneOf', 'TestSession',
			'ConnectedTestSession', 'AuthorizedTestSession', 'TestSessionUtils'
			]
