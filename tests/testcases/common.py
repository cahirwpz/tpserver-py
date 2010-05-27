import collections

from clientsession import ClientSessionHandler

from tp.server.packet import PacketFactory
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

class TestSession( ClientSessionHandler ):#{{{
	NoFailAllowed = True

	def __init__( self ):
		self.bundle = []
		self.count  = 0
		self.status = True
		self.protocol = PacketFactory().objects
		self.scenarioList = []

		self.failRequest  = None
		self.failResponse = None
	
	@logctx
	def sessionStarted( self, transport ):
		super( TestSession, self ).sessionStarted( transport )

		msg( "Connection established.", level="info" )

		self.scenarioList.append( self.__iter__() )

		self.scenario = ichain( *self.scenarioList )
		self.step()

	@logctx
	def packetReceived( self, packet ):
		packet.type = PacketFactory().commandAsString( packet._type )

		msg( "Received ${cyn1}%s${coff} packet." % packet.type, level="info" )

		if self.NoFailAllowed and packet.type == "Fail":
			self.failed( "Fail packet received!" )
			self.failResponse = packet
			self.transport.loseConnection()
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
					self.failed( "Received unexpected packets %s!" % ", ".join( p.type for p in bundle ) )
					self.failResponse = bundle
					self.transport.loseConnection()
				else:
					self.step( bundle )
		elif self.expected and packet not in self.expected:
			self.failed( "Received unexpected packet %s!" % packet.type )
			self.failResponse = packet
			self.transport.loseConnection()
		else:
			self.step( packet )

	def step( self, response = None ):
		try:
			instruction = self.scenario.send( response )
		except StopIteration, ex:
			self.transport.loseConnection()
		else:
			if isinstance( instruction, tuple ):
				request, self.expected = instruction
			else:
				request, self.expected = instruction, None

			self.transport.sendPacket( request )

			self.failRequest = request
			self.failRequest.type = PacketFactory().commandAsString( request.type )

			if request is not None:
				msg( "Sending ${cyn1}%s${coff} packet." % request._name, level="info" )
			
			if isinstance( self.expected, Expect ):
				msg( "${mgt1}Expecting response of type ${wht1}%s${mgt1}.${coff}" % self.expected, level="info" )
	
	def failed( self, reason ):
		self.status = False
		self.reason = reason
#}}}

class ConnectedTestSession( TestSession, IncrementingSequenceMixin ):#{{{
	def __init__( self ):
		super( ConnectedTestSession, self ).__init__()

		self.scenarioList.append( self.__connect() )

	def __connect( self ):
		yield self.protocol.Connect( self.seq, "tpserver-tests client" ), Expect( 'Okay' )
#}}}

class AuthorizedTestSession( TestSession, IncrementingSequenceMixin ):#{{{
	Game		= "tp"
	Login		= "test"
	Password	= "test"

	def __init__( self ):
		super( AuthorizedTestSession, self ).__init__()

		self.scenarioList.append( self.__login() )

	def __login( self ):
		yield self.protocol.Connect( self.seq, "tpserver-tests client" ), Expect( 'Okay' )
		yield self.protocol.Login( self.seq, "%s@%s" % ( self.Login, self.Game), self.Password ), Expect( 'Okay' )
#}}}
