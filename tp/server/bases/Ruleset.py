
class Ruleset(object):
	"""\
	Rulesets define how gameplay works.

	"""

	name = "Unknown Ruleset"

	def __init__(self, game):
		# Now we need to find all the tables and bind it to the correct tables
		self.game = game

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

	def populate(self, *args, **kw):
		"""
		Populate the "universe". It is given a list of arguments.

		All arguments should be documented in the doc string.
		"""
		pass

	def player(self, username):
		"""
		Create a player for this game.
		"""
		board = Board()
		board.id = player.id
		board.name = "Private message board for %s" % player_name
		board.desc = """\
This board is used so that stuff you own (such as fleets and planets) \
can inform you of what is happening in the universe. \
"""
		board.save()

		# Add the first message
		message = Message()
		message.bid = board.id
		message.slot = -1
		message.subject = "Welcome to the Universe!"
		message.body = """\
Welcome, %s, to the python Thousand Parsec server. Hope you have fun! \
""" % (player_name)
		message.save()

		return True

	def turn(self, name):
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
		# Connect to the database
		trans = dbconn.begin()

		try:
			dbconn.use(self.game)
			
			# FIXME: This won't work as if a move then colonise order occurs,
			# and the move order completed the colonise order won't be
			# performed. It also removes the ability for dummy orders to be
			# removed.
			#
			# Get all the orders
			d = {}
			OrderGet(Object(0), d)

			for action in config.order:
				if type(action) == TupleType:
					action, args = action[0], action[1:]
				else:
					args = tuple()
				
				name = str(action.__name__)
				if "orders" in name:
					sys.stdout.write(r"[01;32m")
					print name, args
					sys.stdout.write(r"[00m")
				
					if not d.has_key(name):
						continue

					for order in d[name]:
						order.do(*args)
			
				elif "actions" in name:
					sys.stdout.write(r"[01;34m")
					print name, args
					sys.stdout.write(r"[00m")
				
					__import__(name, globals(), locals(), ["do"]).do(Object(0), *args)
			
			# Reparent the universe
			
		except:
			db.rollback()
			raise
		else:
			db.commit()

