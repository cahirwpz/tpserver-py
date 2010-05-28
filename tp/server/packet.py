from singleton import SingletonClass
from logging import msg

from tp.netlib import parser, structures

import time

def datetime2int( _time ):
	return int( time.mktime( time.strptime( _time.ctime() ) ) )

class PacketFactory( object ):#{{{
	__metaclass__ = SingletonClass

	ProtocolDefinitionFile = "libtpproto2-py/tp/netlib/protocol.xml"

	def __init__( self ):
		self.__objectsById = {}
		self.__commandById = {}

		self.objects = parser.parseFile( PacketFactory.ProtocolDefinitionFile )

		msg("${yel1}Loaded definition for Thousand Parsec Protocol version %d${coff}" % int( self.objects.version[2:]))

		# FIXME: use inspect module
		for name in dir( self.objects ):
			attr = getattr( self.objects, name )

			try:
				self.__objectsById[ attr._id ] = attr
				self.__commandById[ attr._id ] = name
			except AttributeError:
				pass

	def isCommandValid( self, command ):
		return self.__objectsById.has_key( command )

	def commandAsString( self, command ):
		return self.__commandById[ command ]

	def fromBinary( self, command, binary ):
		if self.isCommandValid( command ):
			try:
				packet = self.__objectsById[ command ]()
				packet.unpack( binary )
			except AttributeError, ex:
				msg(ex)
				packet = None
		else:
			packet = None

		return packet

	def fromObject( self, packet, seq, obj ):
		return getattr( self, "make%sPacket" % packet )( seq, obj )

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

	def makeCategoryPacket( self, seq, obj ):
		return self.objects.Category( seq, obj.id, obj.time, obj.name, obj.desc )
	
	def makeComponentPacket( self, seq, obj ):
		return self.objects.Component( seq, obj.id, obj.time, obj.categories,
				obj.name, obj.desc, obj.requirements, obj.properties )

	def makeDesignPacket( self, seq, obj ):
		return self.objects.Design( seq, obj.id, obj.time, obj.categories,
				obj.name, obj.desc, obj.used, obj.owner, obj.components,
				obj.feedback, obj.properties)

	def makeBoardPacket( self, seq, obj ):
		return self.objects.Board( seq, obj.id, obj.name, str(obj.desc).strip(), obj.id, datetime2int( obj.time ) )
		#return self.objects.Board( seq, Board.mangleid( obj.id ), obj.name,
		#		obj.desc, Message.number( obj.id ), self.time)

	def makeMessagePacket( self, seq, obj):
		# FIXME: The reference system needs to be added and so does the turn
		return self.objects.Message( seq, obj.bid, obj.slot, [], obj.subject,
				str(obj.body), 0, [])

	def makeObjectPacket( self, seq, obj ):
		from tp.server.bases.SQLTypedBase import quickimport

		return self.objects.Object( seq, obj.id, quickimport(obj.type).typeno, str(obj.name),
				"Description", 1, obj.contains, 2, 3, [ [[obj.posx, obj.posy,
					obj.posz], -1], [[obj.velx, obj.vely, obj.velz], -1] ] )
				# 1 => parent, 2 => modtime, 3 => padding

	def makePropertyPacket( self, seq, obj ):
		return self.objects.Property( seq, obj.id, obj.time, obj.categories,
				obj.rank, obj.name, obj.displayname, obj.desc, obj.calculate,
				obj.requirements)

	def makeResourcePacket( self, seq, obj ):
		return self.objects.Resource( seq, obj.id, obj.namesingular,
				obj.nameplural, obj.unitsingular, obj.unitplural, obj.desc,
				obj.weight, obj.size, obj.time)

	def makePlayerPacket( self, seq, obj ):
		return self.objects.Player( seq, obj.id, obj.username, "" )

	def makeObjectIDsPacket( self, seq, obj ):
		return self.objects.ObjectIDs( seq, obj.key, obj.left, obj.ids, -1 )
#}}}

"""
	# Taken from Design
	def from_packet(self, user, packet):
		# Check the design meets a few guide lines
		
		# FIXME: Check each component exists and the amount is posative
		for id, amount in packet.components:
			pass
		
		# Check we have at least one category
		if len(packet.categories) < 1:
			raise ValueError("Designs must have atleast one category")
		else:
			# FIXME: Check that the categories are valid
			pass
		
		# FIXME: Check the owner is sane
	
		# FIXME: Check the id
		if packet.id != -1:
			self.id = packet.id
			
		for key in ["categories", "name", "desc", "owner", "components"]:
			setattr(self, key, getattr(packet, key))
"""

def PacketFormatter( packet ):#{{{
	attrs = []

	for structure in packet.structures:
		name = structure.name

		value = structure.__get__(packet, packet.__class__)

		if name == "version":
			try:
				value = "%d.%d" % ( int(value[2:]), 0 )
			except ValueError:
				value = "%d.%d" % ( ord(value[2]), ord(value[3]) )
		elif name == "type":
			value = PacketFactory().commandAsString( packet._type )
		elif isinstance( structure, structures.DateTime.DateTimeStructure ) or (name == "modtime" and type(value) == int):
			value = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))
		elif isinstance( structure, structures.String.StringStructure ): # type(value) in [str, unicode]:
			value = "\"%s\"" % value
		elif isinstance( structure, structures.Enumeration.EnumerationStructure ):
			value = structure.as_string(packet, packet.__class__)
		elif isinstance( structure, structures.Group.GroupStructure ):
			vs = value
			value = []

			for v in vs:
				if v.__class__.__name__ in [ 'GroupProxy', 'GroupStructure', 'ListStructure' ]:
					value.append( list(v) )
				else:
					value.append( v )

		attrs.append( (name.capitalize() + ":", value) )

	column_size = max( map( lambda x: len(x[0]), attrs ) ) + 1

	return "\n".join( [ " %s%s" % (name.ljust(column_size), val) for name, val in attrs ] )
#}}}
