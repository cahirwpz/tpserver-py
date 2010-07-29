#!/usr/bin/env python

#from tp.server.model import DatabaseManager
#from tp.server.packet import PacketFactory, datetime2int
#from version import version as __version__
#from gamemanager import GameManager
#from sqlalchemy import *

from logging import msg
#import os.path, traceback
from collections import Mapping

from tp.server.singleton import SingletonContainerClass

import tp.server.commands

import inspect

class CommandDispatcher( Mapping ):
	__metaclass__ = SingletonContainerClass

	def __init__( self ):
		self.__commands = {}

		for name, cls in inspect.getmembers( tp.server.commands, lambda o: inspect.isclass(o) ):
			msg( "${grn1}Loaded %s command handler.${coff}" % cls.__name__ )

			self.__commands[ name ] = cls
		
	def __getitem__( self, name ):
		return self.__commands[ name ]

	def __iter__( self ):
		return self.__commands.__iter__()

	def __len__( self ):
		return self.__commands.__len__()

__all__ = [ 'CommandDispatcher' ]
