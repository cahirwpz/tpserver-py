from protocol import ThousandParsecProtocol
from logging import logctx, msg
from configuration import ComponentConfiguration, IntegerOption, BooleanOption
from clientsession import ClientSessionHandler

from twisted.internet import reactor, ssl
from twisted.internet.protocol import ServerFactory

from OpenSSL import SSL

class ClientTLSContext( ssl.ClientContextFactory ):
	method = SSL.TLSv1_METHOD

class ThousandParsecServerFactory( ServerFactory, object ):#{{{
	protocol = ThousandParsecProtocol
	noisy = False

	@logctx
	def buildProtocol( self, addr ):
		protocol = ServerFactory.buildProtocol( self, addr )
		protocol.SessionHandlerType = ClientSessionHandler

		return protocol

	@logctx
	def doStart(self):
		msg( "Starting factory." )
		ServerFactory.doStart(self)

		from tp.server import db

		dbconfig = "sqlite:///tp.db"
		dbecho = False

		db.setup(dbconfig, dbecho)

	@logctx
	def doStop(self):
		msg( "Stopping factory." )
		ServerFactory.doStop(self)

	@logctx
	def clientConnectionFailed(self, connector, reason):
		msg( "Connection failed: %s" % reason.getErrorMessage() )

	@logctx
	def clientConnectionLost(self, connector, reason):
		msg( "Connection lost: %s" % reason.getErrorMessage() )

	def configure( self, configuration ):
		self.__tcp_port_num	= configuration.tcp_port
		self.__tls_port_num	= configuration.tls_port
		self.__listen_tls	= configuration.listen_tls

		self.listeners = dict( tcp=None, tls=None )

	def start( self ):
		self.listeners['tcp'] = reactor.listenTCP( self.__tcp_port_num, self )

		if self.__listen_tls:
			self.listeners['tls'] = reactor.listenSSL( self.__tls_port_num, self, ssl.ClientContextFactory() )

	def logPrefix( self ):
		return self.__class__.__name__
#}}}

class ThousandParsecServerConfiguration( ComponentConfiguration ):#{{{
	component	= ThousandParsecServerFactory

	tcp_port	= IntegerOption( short='p', default=6923, min=1, max=65535,
						help='Specifies number of listening port.', arg_name='PORT' )
	tls_port	= IntegerOption( default=6924, min=1, max=65535,
						help='Specifies number of TLS listening port.', arg_name='PORT' )
	listen_tls	= BooleanOption( short='t', default=False,
						help='Turns on TLS listener.' )
#}}}

"""
import weakref
servers = weakref.WeakValueDictionary()

class FullServer(netlib.Server):
	# FIXME: Should start a thread for ZeroConf registration...
	handler = FullConnection
	debug = config.socketecho

	def __init__(self, *args, **kw):
		netlib.Server.__init__(self, *args, **kw)

		# Add us to the server list...
		servers[__builtins__['id'](self)] = self

		# Remove any order mapping from the network libray...
		netlib.objects.OrderDescs().clear()

		try:
			import signal

			# Make sure this thread gets these signals...
			signal.signal(signal.SIGTERM, self.shutdown)
			#signal.signal(signal.SIGKILL, self.exit)
			signal.signal(signal.SIGINT,  self.shutdown)
		except ImportError:
			print "Unable to set up UNIX signalling."

		# The thread for discovering this server
		from discover import DiscoverServer
		self.discover = DiscoverServer(metaserver)

		self.events = Event.latest()

		# Register all the games..
		self.locks  = []
		for id, time in Game.ids():
			self.gameadded(Game(id))

	def poll(self):
		# Get any new events..
		for event in Event.since(self.events):
			print 'New Event!!! -->', event

			if hasattr(self, event.eventtype):
				try:
					getattr(self, event.eventtype)(Game(event.game))
				except Exception, e:
					print e
			
			self.events = event.id

	def gameadded(self, g):
		already = [lock.game for lock in self.locks]
		if g.id in already:
			print "Got gameadded event for a game I already have a lock on!"
			return

		# Create a lock for this game
		db.dbconn.use(g)
		self.locks.append(Lock.new('serving'))
		db.dbconn.commit()

		# Setup the game
		g.ruleset.setup()

		# Make the game discoverable	
		self.discover.GameAdd(g.to_discover())

		db.dbconn.commit()

	def gameremoved(self, g):
		toremove = None
		for lock in self.locks:
			if lock.game == g.id:
				toremove = lock
				break
		
		if toremove is None:
			print "Got gameremoved event for a game I didn't have a lock on!"
			return

		self.discover.GameRemove(g.to_discover())
			
		self.locks.remove(toremove)
		del toremove

		db.dbconn.commit()

		print "Game remove!", g

	def endofturn(self, game):
		# Send TimeRemaining Packets
		packet = netlib.objects.TimeRemaining(0, -1)

		for connection in self.connections.values():
			if isinstance(connection, FullConnection) and not connection.user is None:
				if connection.user.game != game.id:
					continue

				print "Sending EOT to", connection
				connection._send(packet)

	def shutdown(self, *args, **kw):
		# Remove the locks
		del self.locks

		# Close the discover threads
		self.discover.exit()
		
		# Exit this thread...
		import sys
		sys.exit()
	
	def serve_forever(self):
		# Start the discover threads..
		self.discover.start()

		# Need to wake up to check for things like EOT
		netlib.Server.serve_forever(self, 400)
"""
