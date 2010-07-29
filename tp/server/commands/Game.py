#!/usr/bin/env python

class GameFactoryMixin( object ):
	@property
	def server_version( self ):
		return "%d.%d.%d" % (0,4,0)

	@property
	def server_software( self ):
		return "tpserver-py"

	@property
	def locations( self ):
		servername	= "localhost"
		serverip	= "127.0.0.1"
		port		= "6923"

		locations = []
		locations.append(('tp',       servername, serverip, port))
		#locations.append(('tp+http',  servername, serverip, port))
		#locations.append(('tps',      servername, serverip, port))
		#locations.append(('tp+https', servername, serverip, port))

	def makeGamePacket( self, seq, obj ):
		return self.objects.Game( seq, obj.longname, obj.key, ["0.3", "0.3+"],
				self.server_version, self.server_software, obj.ruleset.name,
				obj.ruleset.version, self.locations, obj.parameters)

