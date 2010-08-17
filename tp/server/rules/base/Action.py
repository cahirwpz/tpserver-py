#!/usr/bin/env python

from tp.server.rules.base.utils import OrderGet
from logging import *

class Action( object ):
	def __call__( self, *args, **kwargs ):
		pass

class UniverseAction( object ):
	"""
	Anything that happens without requiring the user to initiate.
	Some examples would be Combat or growing the Population.
	"""

	def __walk( self, top, order, callback, *args, **kwargs ):
		"""
		Walks around the universe and calls a command for each object.
		
		If the first argument is "before" parents will be called before there children.
		If the first argument is "after" parents will be called after there children.
		"""
		if order == "before":
			callback(top, *args, **kwargs)

		for id in top.contains():
			self.__walk(Object(id), order, callback, *args, **kwargs)

		if order == "after":
			callback(top, *args, **kwargs)

	def __call__( self, top, order, callback, *args, **kwargs ):
		"""
		Given the universe as an interable object. It impliments most
		functions of dictionaries.
		A parent will appear before it's child.
		"""
		self.__walk( top, order, callback, *args, **kwargs )

class ActionProcessor( object ):
	def __init__( self, ruleset ):
		self.ruleset = ruleset

	def turn( self ):
		"""
		generate a turn for this ruleset

		For simple rulesets (and some reasonably complicated ones), this default
		method works.

		This method performs orders and actions in the order dictated via the 
		orderOfOrders attribute. The program treats actions and orders almost 
		identically.

		For example, 
			If orderOfOrders contained,
				[MoveAction, Nop, (Clean, 'fleetsonly')]
			The move action would be applied first.
			Then all NOp orders would be performed.
			Then the Clean action would be applied with the argument ('fleetsonly')
		"""
		Lock, Object, Event = self.model.use( 'Lock', 'Object', 'Event' )

		# Create a turn processing lock
		lock = Lock.new('processing')

		# FIXME: This won't work as if a move then colonise order occurs,
		# and the move order completed the colonise order won't be
		# performed. It also removes the ability for dummy orders to be
		# removed.
		#
		# Get all the orders

		d = OrderGet()

		print d

		for action in self.orderOfOrders:
			if isinstance( action, tuple ):
				action, args = action[0], action[1:]
			else:
				args = tuple()
			
			name = str(action.__name__)
			if "orders" in name:
				debug("%s - Starting with" % name, args)
			
				if d.has_key(name):
					for order in d[name]:
						order.do(*args)
				else:
					debug( "No orders of that type avaliable.." )

				debug("%s - Finished" % name)
		
			elif "actions" in name:
				debug("%s - Starting with" % name, args)
			
				__import__(name, globals(), locals(), ["do"]).do(Object(0), *args)

				debug("%s - Finished" % name)
		
		# Reparent the universe

		# Create a EOT event
		Event.new('endofturn', self.game)

__all__ = [ 'Action', 'UniverseAction', 'ActionProcessor' ]
