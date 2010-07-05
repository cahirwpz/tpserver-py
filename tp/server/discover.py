
import threading

from tp.netlib.discover.server import Server

class DiscoverServer(Server):
	def start(self):
		self.local.start()

		if not self.remote.server is None:
			self.remote.start()

	def exit(self):
		self.local.exit()
		self.remote.exit()

	def GameAdd(self, game):
		self.local.GameAdd(game)
		self.remote.GameAdd(game)

	def GameUpdate(self, game):
		self.local.GameUpdate(game)
		self.remote.GameUpdate(game)

	def GameRemove(self, game):
		self.local.GameRemove(game)
		self.remote.GameRemove(game)

"""
	def to_discover(self):
		g = DiscoverGame(self.longname)

		from tp.server.server  import servers, servername, serverip
		from tp.server.version import version

		required = {}
		required['key']     = self.key
		required['tp']      = "0.3,0.3+"
		required['server']  = "%s.%s.%s" % version[0:3]
		required['sertype'] = "tpserver-py"
		required['rule']    = self.ruleset.name
		required['rulever'] = self.ruleset.version
		g.updateRequired(required)

		for server in servers.values():
			for port in server.ports:
				g.addLocation('tp',       (servername, serverip, port))
				g.addLocation('tp+http',  (servername, serverip, port))
			for port in server.sslports:
				g.addLocation('tps',      (servername, serverip, port))
				g.addLocation('tp+https', (servername, serverip, port))

		# Build the optional parameters
		optional = {}
		# FIXME: Magic Numbers!
		# Number of players
		optional['plys']  = self.players
		# Number of objects
		optional['objs']  = self.objects
		# Admin email address
		optional['admin'] = self.admin
		# Comment
		optional['cmt']   = self.comment
		# Turn
		#optional.append((6, '', self.turn))

		g.updateOptional(optional)
		return g
"""
