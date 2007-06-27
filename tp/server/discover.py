
import threading

from tp.netlib.discover.server import Server
from tp.netlib.discover import LocalServer as LocalServerB
from tp.netlib.discover import RemoteServer as RemoteServerB
class LocalServer(LocalServerB, threading.Thread):
	def __init__(self, *args, **kw):
		threading.Thread.__init__(self)
		LocalServerB.__init__(self, *args, **kw)

class RemoteServer(RemoteServerB, threading.Thread):
	def __init__(self, *args, **kw):
		threading.Thread.__init__(self)
		RemoteServerB.__init__(self, *args, **kw)

class DiscoverServer(Server):
	def __init__(self, metaserver):
		self.local  = LocalServer()
		self.remote = RemoteServer(metaserver)

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
