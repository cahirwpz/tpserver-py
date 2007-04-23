
class Ruleset(object):
	name = "Unknown Ruleset"

	def __init__(self, database, name):
		"""\
		database - database connection to use
		name     - unique name of the game, this MUST be unique per server
		"""
		self.database = database
		self.name     = name

		# Now we need to find all the tables and bind it to the correct tables
		

	def game(self, database, name, **kw):
		""" 
		Create a new game of this type.
		
		optional arguments which are ruleset specific.
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
		Generate a new turn.
		"""
		# Connect to the database
		db.begin()

		try:
			# Use the corret database
			db.query("USE %(database)s", database=sys.argv[1])
			
			# Clean up any phoney orders

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

