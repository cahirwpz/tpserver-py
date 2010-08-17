#!/usr/bin/env python

from singleton import SingletonContainerClass
from logging import msg

from tp.netlib import parser, structures

import inspect, time

from collections import Mapping

class ProtocolPackets( Mapping ):#{{{
	def __init__( self, filename ):
		packets = parser.parseFile( filename )

		self.__byId   = {}
		self.__byName = {}

		for name, cls in inspect.getmembers( packets, inspect.isclass ):
			if hasattr( cls, '_id' ):
				self.__byId[ cls._id ] = cls
				self.__byName[ name ] = cls

		self.__version = packets.version

	@property
	def version( self ):
		return self.__version

	def use( self, *names ):
		if len( names ) == 1:
			return self.__byName[ names[0] ]
		else:
			return tuple( self.__byName[ name ] for name in names )

	def __getitem__( self, key ):
		if isinstance( key, str ):
			return self.__byName[ key ]
		elif isinstance( key, int ):
			return self.__byId[ key ]
		else:
			raise TypeError( "PacketTypes container can be indexed by %s or %s only" % ( int, str ) )

	def __iter__( self ):
		return self.__byName.__iter__()

	def __len__( self ):
		return self.__byName.__len__()
#}}}

ProtocolDefinitionFiles = [
	( "TP03", "libtpproto2-py/tp/netlib/protocol3.xml" ),
	( "TP\x04\x00", "libtpproto2-py/tp/netlib/protocol.xml" ) ]

class PacketFactory( Mapping ):#{{{
	__metaclass__ = SingletonContainerClass

	def __init__( self ):
		self.__protocol = {}

		for version, filename in ProtocolDefinitionFiles:
			protocol = ProtocolPackets( filename )

			self.__protocol[ version ] = protocol

			msg("${yel1}Loaded definition for Thousand Parsec Protocol version %s.${coff}" % protocol.version )

	def __getitem__( self, version ):
		if version == 'default':
			version = "TP03"

		return self.__protocol.__getitem__( version )

	def __iter__( self ):
		return self.__protocol.__iter__()

	def __len__( self ):
		return self.__protocol.__len__()

	def fromBinary( self, version, command, binary ):
		try:
			packet = self.__protocol[ version ][ command ]()
			packet.unpack( binary )
		except AttributeError, ex:
			msg(ex)
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
				value = "%d.%d" % ( ord(value[2]), ord(value[3]) )
		elif name == "type":
			value = packet.__class__.__name__
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

__all__ = [ 'PacketFactory', 'PacketFormatter' ]
