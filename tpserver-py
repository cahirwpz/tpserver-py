
current_turn = 1
game_base = 'test_game'

import os
import sys
import string
import cPickle as pickle

sys.path.append(os.path.join("..", "common"))

from universe import Map
from player import Player

if __name__ == '__main__':

	###############
	# Load the config file, get command line arguments
	###############
	CONFIG = {}
	CONFIG['NoTurn'] = 1
	CONFIG['UnAttended'] = 1
	CONFIG['Overwrite'] = 1

	###############
	# Load the main map 'Map.<current_turn-1>'
	###############

	map_location = os.path.join(game_base, "Map.t%d" % (current_turn-1))

	if not os.path.exists(map_location):
		raise SyntaxError, "Could not find the previous turns map file! (%s)" % (map_location)

	f = open(map_location)
	UNIVERSE = pickle.load(f)

	###############
	# Load the player list from 'Players.<current_turn - 1>'
	###############

	player_location = os.path.join(game_base, "Players.t%d" % (current_turn-1))

	if not os.path.exists(player_location):
		raise SyntaxError, "Count not find the previous turns player list! (%s)" % (player_location)

	f = open(player_location)
	PLAYERS = pickle.load(f)

	###############
	# Load all the 'Incoming/In.<player ID>.<current_turn - 1>'
	# Set origin of the Messages
	###############

	player_location = os.path.join(game_base, "Incoming", "In.%%s.t%d" % (current_turn-1))

	INCOMING = {}

	print "Players in the current game", PLAYERS

	for player in PLAYERS.values():
		# Check the player has submited there turn file
		if not os.path.exists(player_location % (player.id)):

			# Ekk the player didn't submit his turn file!
			if not CONFIG['NoTurn'] and CONFIG['Unattended']:
				# The admin hasn't specified to continue anyway and it's unattended so exit!
				error = """\
				Could not find player's (%s) turn file! (%s)
				If you would like the server to continue
				anyway put the following in the config file:

				NoTurn = TRUE

				"""
				raise SyntaxError, error % (player.id, player_location % (player.id))

			elif not CONFIG['NoTurn']:
				# The admin hasn't specified to continue so ask him
				error = """\
				Could not find player's (%s) turn file! (%s)
				If you would like the server to continue
				without asking put the following in the
				config file:

				Unattended = TRUE

				Would you like to continue? (Yes/No/All)
				"""
				sys.stdout.write(error % (player.id, player_location % (player.id)))

				while TRUE:
					response = sys.stdin.readline()
					response = string.strip(response)
					response = response[0]

					if response == 'N':
						raise SyntaxError, "See above!"
					elif response == 'A':
						CONFIG['Unattended'] == TRUE
						break
					elif response == 'Y':
						break
			else:
				player_INCOMING = []
		else:
			# Okay load the file
			f = open(player_location % (player.id))
			player_INCOMING = pickle.load(f)

		for message in player_INCOMING:
			# Set the origin of the files
			message.origin = player.base

		INCOMING[player.id] = player_INCOMING

	###########
	# Load the 'Incoming.<current_turn - 1>' queue
	###########

	incoming_location = os.path.join(game_base, "Incoming.t%d" % (current_turn-1))

	if not os.path.exists(incoming_location):
		raise SyntaxError, "Count not find the previous turns Incoming Queue! (%s)" % (incoming_location)

	f = open(incoming_location)
	IN_QUEUE = pickle.load(f)

	###########
	# Merge Players queue into the main queue
	###########

	for player in PLAYERS.values():
		for message in INCOMING[player.id]:
			# FIXME: Need to put consitancy checks in here
			IN_QUEUE.append(message)

	del INCOMING

	###########
	# Move Incoming messages around
	###########

	for message in IN_QUEUE:
		UNIVERSE.getByID(message.dst).orders.append[message]

	###########
	# Load the out going queue, 'Outgoing.<current_turn - 1>'
	###########

	outgoing_location = os.path.join(game_base, "Outgoing.t%d" % (current_turn-1))

	if not os.path.exists(outgoing_location):
		raise SyntaxError, "Count not find the previous turns Outgoing Queue! (%s)" % (outgoing_location)

	f = open(outgoing_location)
	OUT_QUEUE = pickle.load(f)

	#################################################################
	# Main generation Phase, output to the outgoing queue
	#################################################################

	#################################################################
	#################################################################

	smart_objects = []

	for system in UNIVERSE.getAll():
		for object in system:
			if hasattr(object, 'orders'):
				smart_objects.append(object) 

	# Smart objects now contains all the objects with orders
	from orders import *
	from types import StringType

	order = [COMBAT, MOVE, TRACKING, MISC, 'POPULATION', 'MINING', TRANSPORT_DROP, BUILD, TRANSPORT_PICKUP, MOVE, COMBAT, SCANNING]

	while len(order):
		order_type = order.pop()

		if type(order_type) != StringType:

			# We have a normal order type so we need to extract objects which have the orders we are currently processing
			current_objects = []

			for object in smart_objects:
				if issubclass(object.orders[0], order_type):
					current_objects.append(object)
					object.remaining = 100

			for object in current_objects:
				# Do the order
				object.remaining, result, finished = object.order.do(object.remaining)

				if results != None:
					OUTGOING.append(result)

				if finished:
					# The order has finished so nuke it
					object.order.pop()

		else:
			if order_type == 'POPULATION':
				for system in UNIVERSE.getAll():
					for object in system:
						if isinstance(object, Planet):
							# Population grows in Planets
							pass
						elif isinstace(object, Ship):
							# Population can grow in ships under certain conditions
							pass

			elif order_type == 'MINING':
				for system in UNIVERSE.getAll():
					for object in system:
						if isinstance(object, Planet):
							# Mining occurs on a Planet if mines exist on it
							pass

						elif isinstace(object, Ship):
							# Check if the ship has mining orders
							if object.orders[0].type == MINING:
								pass

	###########
	# Call any custom hooks
	###########


	###########
	# Deliver Outgoing messages
	###########

	OUTGOING = {}

	for player in PLAYERS.values():
		OUTGOING[player.id] = []

	for message in OUT_QUEUE:

		# Deliver messages to the players
		if message.dst in PLAYERS.keys():
			OUTGOING[message.dst].append(message)
		else:
			# Else deliver them to the incoming queue
			IN_QUEUE.append(message)

	###########
	# Write out 'Incoming.<current_turn>' queue
	###########
	incoming_location = os.path.join(game_base, "Incoming.t%d" % (current_turn))

	if os.path.exists(incoming_location) and not CONFIG['Overwrite']:
		raise IOError,  "The Incoming file for this turn already exists! (%s)" % incoming_location
	elif os.path.exists(incoming_location):
		# Delete the file
		os.remove(incoming_location)
	
	f = open(incoming_location, 'w+')
	pickle.dump(IN_QUEUE, f)

	# Cleanup
	del IN_QUEUE

	###########
	# Write out the player files 'Outgoing/Out.<player ID>.<current_turn>'
	###########

	player_location = os.path.join(game_base, "Outgoing", "Out.%%s.t%d" % (current_turn))

	for player in PLAYERS.values():
		if os.path.exists(player_location % (player.id)) and not CONFIG['Overwrite']:
			raise IOError, "The players turn file already exists! (%s)" % (player_location % player.id)
		elif os.path.exists(player_location % (player.id)):
			# Delete the file
			os.remove(player_location % (player.id))
			
		f = open(player_location % (player.id), 'w+')
		pickle.dump(OUTGOING[player.id], f)
		

	###########
	# Write out the outgoing queue, 'Outgoing.<current_turn>'
	###########

	outgoing_location = os.path.join(game_base, "Outgoing.t%d" % (current_turn))
	if os.path.exists(outgoing_location) and not CONFIG['Overwrite']:
		raise IOError, "The Outgoing file for this turn already exists! (%s)" % outgoing_location
	elif os.path.exists(outgoing_location):
		# Delete the file
		os.remove(outgoing_location)

	f = open(outgoing_location, 'w+')
	pickle.dump(OUT_QUEUE, f)
	# Cleanup
	del OUT_QUEUE
	del OUTGOING

	###########
	# Load new players from player 'New/<player ID>.rdf'
	###########

	###########
	# Generate the starting stuff for the player
	###########

	# 1. Find a home world(s) with very close stats and so far away from any other players worlds

	# . Place player in PLAYERS

	# . Nuke any previous stuff on planet

	# . Change home world to be perfect for the race

	# . Up the mineral concentration to a good range

	# . Place starting popuplation/factories/mines on planet

	# . Place starting ships around planet

	# . Do other stuff :)

	# . Create a Outgoing Out file with successfully joined message, homeworld location

	# . Create a dummy Incoming In file for next turn.


	### Therefore it takes 2 turns to join.
	###
	### 1st turn inserts the player into the universe
	### 2nd turn gives the player all the information it needs
	### 3rd turn is like every other

	###########
	# Write out 'Players.<current_turn>'
	###########
	player_location = os.path.join(game_base, "Players.t%d" % (current_turn))
	if os.path.exists(player_location) and not CONFIG['Overwrite']:
		raise IOError, "Players file already exists for this turn! (%s)" % player_location
	elif os.path.exists(player_location):
		# Delete the file
		os.remove(player_location)
		
	f = open(player_location, 'w+')
	pickle.dump(PLAYERS, f)


	###########
	# Write out 'Map.<current_turn>'
	###########
	map_location = os.path.join(game_base, "Map.t%d" % (current_turn))
	if os.path.exists(map_location) and not CONFIG['Overwrite']:
		raise IOError, "Map file already exists for this turn! (%s)" % map_location
	elif os.path.exists(map_location):
		#Delete the file
		os.remove(map_location)
		
	f = open(map_location, 'w+')
	pickle.dump(UNIVERSE, f)
