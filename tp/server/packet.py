from singleton import SingletonClass
from logging import msg

from tp.netlib import parser, structures

import time

class PacketFactory( object ):#{{{
	__metaclass__ = SingletonClass

	ProtocolDefinitionFile = "libtpproto2-py/tp/netlib/protocol3.xml"

	def __init__( self ):
		self.__objectsById = {}
		self.__commandById = {}

		self.objects = parser.parseFile( PacketFactory.ProtocolDefinitionFile )

		msg("${yel1}Loaded definition for Thousand Parsec Protocol version %d${coff}" % int( self.objects._version[2:]))

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
#}}}

def PacketFormatter( packet ):#{{{
	attrs = []

	for structure in packet.structures:
		name = structure.name

		value = structure.__get__(packet, packet.__class__)

		if name == "version":
			try:
				value = "%d.%d" % ( int(value[2:]), 0 )
			except ValueError:
				value = "%d.%d" % ( value[2], value[3] )
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
