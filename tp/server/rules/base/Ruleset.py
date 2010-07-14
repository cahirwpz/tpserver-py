#!/usr/bin/env python

import sys
from types import TupleType

from tp.server.db import DatabaseManager
from tp.server.utils import OrderGet

class Ruleset(object):#{{{
	"""
	Rulesets define how gameplay works.
	"""
	name    = "Unknown Ruleset"
	version = 'Unknown Version'

	def __init__(self, game = None):
		"""
		Initialise a ruleset.
		"""
		self.game = game
		#self.setup()

	@property
	def information( self ):
		return [ ('name',    self.name ),
				 ('version', self.version),
				 ('comment', "\n".join( map( str.strip, self.__doc__.strip().splitlines() ))) ]
	
	def __str__( self ):
		return "%s, version %s" % (self.name, self.version)

	def setup(self):
		"""
		Sets up the game after a restart.

		All orders needed by the module should be imported and registered with
		the ruleset.

		All objected needed by the module should be imported and registered with 
		the ruleset.

		By default it will setup all orders in the orderOfOrders.
		"""
		self.ordermap = {}
		for action in self.orderOfOrders:
			if type(action) == TupleType:
				action, args = action[0], action[1:]
			else:
				args = tuple()
			
			name = str(action.__name__)
			if "orders" in name:
				order = getattr(action, name.split('.')[-1])

				if name in [x.__module__ for x in self.ordermap.values()]:
					continue

				if not hasattr(order, 'typeno'):
					typeno = len(self.ordermap) + 1
				else:
					typeno = order.typeno

				if self.ordermap.has_key(typeno):
					raise TypeError('Two orders (%s and %s) have conflicting type numbers!' % (self.ordermap[typeno].__module__, order.__module__))

				self.ordermap[typeno] = order 

		self.objectmap = {}

	def typeno(self, cls):
		"""
		Returns the typeno for a class.
		"""
		# FIXME: There should be a better way to do this
		for typeno, order in self.ordermap.items():
			if str(order.__module__) == str(cls.__module__):
				return typeno
		for typeno, order in self.objectmap.items():
			if str(order.__module__) == str(cls.__module__):
				return typeno

	def initialise(self):
		""" 
		Initialise the database with anything needed for this game.

		The ruleset should do things like,
			- Create any components in the databases
			- Create any resources in the databases
			- etc

		This should not add anything to the players universe. Use the populate
		command for that.

		This command takes no arguments, so it should not do anything which 
		needs information from the user.
		"""
		pass

	def update(self):
		"""
		Update an in progress game with the data that is current only disk.
		"""
		pass

	def populate(self, *args, **kw):
		"""
		Populate the "universe". It is given a list of arguments.

		All arguments should be documented in the doc string.
		"""
		pass

	def player( self, username, password, email = 'N/A', comment = '' ):
		"""
		Create a player for this game.

		The default function creates a new user, a board for the user and adds a
		welcome message. It returns the newly created user object.
		"""
		Player, Board, Message, Slot = self.game.objects.use( 'Player', 'Board', 'Message', 'Slot' )

		player = Player(
			username	= username,
			password	= password,
			email		= email,
			comment		= comment)

		board = Board(
			owner		= player,
			name        = "Private message board for %s" % username,
			description = "This board is used so that stuff you own (such as fleets and planets) can inform you of what is happening in the universe.")

		message = Message(
			subject = "Welcome to the Universe!",
			body    = "Welcome, %s, to the python Thousand Parsec server. Hope you have fun!" \
					  "This game is currently playing version %s of %s." % ( username, self.version, self.name ))

		slot = Slot(
			message	= message,
			board	= board,
			number	= 0)

		with DatabaseManager().session() as session:
			session.add( player )
			session.add( board )
			session.add( message )
			session.add( slot )

		return player

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
		# Create a turn processing lock
		#lock = Lock.new('processing')

		with DatabaseManager().session() as session:
			# FIXME: This won't work as if a move then colonise order occurs,
			# and the move order completed the colonise order won't be
			# performed. It also removes the ability for dummy orders to be
			# removed.
			#
			# Get all the orders
			d = OrderGet()
			print d
			for action in self.orderOfOrders:
				if type(action) == TupleType:
					action, args = action[0], action[1:]
				else:
					args = tuple()
				
				name = str(action.__name__)
				if "orders" in name:
					green("%s - Starting with" % name, args)
				
					if d.has_key(name):
						for order in d[name]:
							order.do(*args)
					else:
						print "No orders of that type avaliable.."

					green("%s - Finished" % name)
			
				elif "actions" in name:
					blue("%s - Starting with" % name, args)
				
					__import__(name, globals(), locals(), ["do"]).do(Object(0), *args)

					blue("%s - Finished" % name)
			
				sys.stdout.write("\n")

			# Reparent the universe

			# Create a EOT event
			Event.new('endofturn', self.game)
#}}}

__all__ = [ 'Ruleset' ]
