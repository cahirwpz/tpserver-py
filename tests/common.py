#!/usr/bin/env python

import new, time
from unittest import TestCase
from logging import debug, info, error, exception
from twisted.internet import reactor

from tp.server.packet import PacketFactory, PacketFormatter

from clientsession import ClientSessionHandler
from client import ThousandParsecClientFactory

def ichain( *args ):
	for a in args:
		try:
			r = None
			while True:
				r = yield a.send(r)
		except StopIteration:
			pass

class Expect( object ):
	def __init__( self, packet ):
		assert isinstance( packet, str )

		self.__packet = packet

	def __eq__( self, response ):
		return response.type == self.__packet

	def __ne__( self, response ):
		return not (self == response)

	def __str__( self ):
		return self.__packet

class ExpectFail( Expect ):
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

class ExpectSequence( Expect ):
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

class ExpectOneOf( Expect ):
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

class TestSessionMetaClass( type ):
	def __call__( cls, *args, **kwargs ):
		instance = cls.__new__( cls )
		instance.__init__( *args, **kwargs )

		setUpMethods    = []
		tearDownMethods = []

		for _cls in reversed( cls.__mro__ ):
			setUp    = getattr( _cls, 'setUp', None )
			tearDown = getattr( _cls, 'tearDown', None )

			if setUp:
				if not len( setUpMethods ) or setUp != setUpMethods[-1]:
					setUpMethods.append( setUp )

			if tearDown:
				if not len( tearDownMethods ) or tearDown != tearDownMethods[0]:
					tearDownMethods.insert( 0, tearDown )

		def chain( methods ):
			def fun( self ):
				for method in methods:
					method( self )
			return fun

		instance.setUp    = new.instancemethod( chain( setUpMethods ), instance, cls )
		instance.tearDown = new.instancemethod( chain( tearDownMethods ), instance, cls )

		return instance 

class TestSession( TestCase, ClientSessionHandler ):
	__metaclass__ = TestSessionMetaClass

	def __init__( self, *args, **kwargs ):
		super( TestSession, self ).__init__( *args, **kwargs )

		self.bundle		= []
		self.count 		= 0
		self.protocol	= PacketFactory()["TP03"]
		self.scenarioList = []

		self.reason		= None
		self.request	= None
		self.response	= None
		self.expected	= None

		self.__finished = False

	@staticmethod
	def datetimeToInt( t ):
		return long( time.mktime( time.strptime( t.ctime() ) ) )
	
	def setUp( self ):
		debug( "Setting up %s test...", self.__class__.__name__ )

		reactor.__init__()
		ThousandParsecClientFactory().makeTestSession( self )
	
	def tearDown( self ):
		debug( "Tearing down %s test...", self.__class__.__name__ )

	def runTest( self ):
		debug( "Starting %s test...", self.__class__.__name__ )
		reactor.run()
		debug( "Finished %s test...", self.__class__.__name__ )

		if self.reason:
			self.fail( self.reason )
	
	def sessionStarted( self, transport ):
		super( TestSession, self ).sessionStarted( transport )

		debug( "Connection established." )

		if hasattr( self, '__iter__' ):
			self.scenarioList.append( self.__iter__() )

		self.scenario = ichain( *self.scenarioList )

		self.step()

	def packetReceived( self, packet ):
		packet.type = packet.__class__.__name__

		debug( "Received %s packet.", packet.type )

		if packet.type == "Sequence":
			self.count = packet.number
			self.bundle.append( packet )
		elif self.count > 0:
			self.bundle.append( packet )
			self.count -= 1

			if self.count == 0:
				self.step( self.bundle )

				self.bundle = []
		else:
			self.step( packet )

	def step( self, response = None ):
		if not self.__finished:
			try:
				self.response = response
				request = self.scenario.send( response )
			except StopIteration as ex:
				self.succeeded()
			except AssertionError as ex:
				self.failed( str(ex) )
			except Exception as ex:
				exception( "Exception %s(%s) caught!" % (ex.__class__.__name__, str(ex)) )
				self.failureException = ex.__class__
				self.failed( str(ex) )
			else:
				self.transport.sendPacket( request )

				self.request = request
				self.request.type = request.__class__.__name__

				if request is not None:
					debug( "Sending %s packet.", request._name )
				
	def failed( self, reason ):
		if not self.__finished:
			self.__finished = True

			self.transport.loseConnection()

			self.reason = reason

			error( self.reason )

			if self.request:
				error( "Failing request %s:", self.request.type )
				error( PacketFormatter( self.request ) )

			if self.response:
				if isinstance( self.response, list ):
					error( "Wrong response %s:", ", ".join( r.type for r in self.response ) )
					for r in self.response:
						error( "Packet:" )
						error( PacketFormatter( r ) )
				else:
					error( "Wrong response %s:", self.response.type )
					error( PacketFormatter( self.response ) )

			if self.expected:
				error( "Expected:\n %s", self.expected )

			reactor.callLater( 0, lambda: reactor.stop() )

	def succeeded( self ):
		if not self.__finished:
			self.__finished = True

			self.transport.loseConnection()

			reactor.callLater( 0, lambda: reactor.stop() )

	def assertPacketType( self, packet, expected, reason = None ):
		if packet != expected:
			self.expected = expected
			raise AssertionError( reason )

	def assertPacket( self, packet, expected, reason = None ):
		self.assertPacketType( packet, Expect( expected ), reason )

	def assertPacketFail( self, packet, expected, reason = None ):
		self.assertPacketType( packet, ExpectFail( expected ), reason )
	
__all__ = [ 'Expect', 'ExpectFail', 'ExpectSequence', 'ExpectOneOf', 'TestSession' ]
