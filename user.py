
import sys
sys.path.append("../")

import math

import db

from sobjects.Board   import Board
from sobjects.Message import Message
from sobjects.Object  import Object
from sobjects.Order   import Order
from sobjects.User    import User

def add(username, password):

	# Check the user doesn't already exist
	if User.realid(username) != -1:
		print "User already exists!"
		return
	
	# Add a new user
	user = User()
	user.username = username
	user.password = password
	user.insert()
	print "User has the id:", user.id

	# Add private message board
	board = Board()
	board.id = user.id
	board.name = "Private message board for %s" % username
	board.desc = """\
This board is used so that stuff you own (such as fleets and planets) \
can inform you of what is happening in the universe. \
"""
	board.insert()
	print "Board has the id:", board.id

	# Add the first message
	message = Message()
	message.bid = board.id
	message.slot = -1
	message.subject = "Welcome to the Universe!"
	message.body = """\
Welcome, %s, to the python Thousand Parsec server. Hope you have fun! \
""" % username
	message.insert()
	print "First message has the id:", message.id

	# Generate a position for the homeworld...
	import random
	SIZE = 10000000000
	pos = random.randint(SIZE*-1, SIZE), random.randint(SIZE*-1, SIZE), random.randint(SIZE*-1, SIZE)
	print "Putting homeworld at", pos

	# Add homesystem
	homesystem = Object()
	homesystem.type = 2
	homesystem.name = "%s's System" % username
	homesystem.size = random.randint(800000, 2000000)
	homesystem.parent = 0
	homesystem.posx = pos[0]
	homesystem.posy = pos[1]
	homesystem.posz = pos[2]
	homesystem.velx = 0
	homesystem.vely = 0
	homesystem.velz = 0
	homesystem.insert()
	print "Homeworld has the id:", homesystem.id
	
	# Add homeworld
	homeworld = Object()
	homeworld.type = 3
	homeworld.name = "%s's Homeworld" % username
	homeworld.size = 1000
	homeworld.parent = homesystem.id
	homeworld.posx = pos[0]
	homeworld.posy = pos[1]
	homeworld.posz = pos[2]
	homeworld.velx = 0
	homeworld.vely = 0
	homeworld.velz = 0
	homeworld.owner = user.id
	homeworld.insert()
	print "Homeworld has the id:", homeworld.id

	# Add some other planets just for fun!
	extraplanets = random.randint(0, 5)
	print "Adding %s planet's for fun!" % extraplanets

	for planet in range(0, extraplanets):
		extra = Object()
		extra.type = 3
		extra.name = "Unknown planet"
		extra.size = random.randint(1000, 10000)
		extra.parent = homesystem.id
		extra.posx = pos[0]
		extra.posy = pos[1]
		extra.posz = pos[2]
		extra.velx = 0
		extra.vely = 0
		extra.velz = 0
		extra.owner = 0
		extra.insert()
		print "Extra planet has the id:", extra.id

	# Add inital fleet
	fleet = Object()
	fleet.type = 4
	fleet.name = "First Fleet"
	fleet.size = 1
	fleet.parent = homeworld.id
	fleet.posx = homeworld.posx
	fleet.posy = homeworld.posy
	fleet.posz = homeworld.posz
	fleet.velx = 0
	fleet.vely = 0
	fleet.velz = 0
	fleet.owner = user.id
	fleet.insert()
	print "Fleet has the id:", fleet.id
	
def main():
	# Connect to the database
	db.connect()

	if sys.argv[1] == "--add":
		username, password = sys.argv[2], sys.argv[3]
		add(username, password)
	elif sys.argv[1] == "--delete":
		username = sys.argv[2]
		delete(username)
	elif sys.argv[1] == "--clear":
		# Delete all the created objects
		db.query("DELETE FROM tp.object WHERE id > 28")

		# Delete all the create object attributes
		db.query("DELETE FROM tp.object_attr WHERE object_id > 0")

		# Delete all the created orders
		db.query("DELETE FROM tp.order")

		# Delete all the create order attributes
		db.query("DELETE FROM tp.order_attr")

		# Delete all the created boards
		db.query("DELETE FROM tp.board WHERE id > 0")

		# Delete all the create messages
		db.query("DELETE FROM tp.message")

		# Delete all from the user table
		db.query("DELETE FROM tp.user")

	else:
		print "Unknown operation."
	
if __name__ == "__main__":
	main()


