
import sys
import os
import cPickle as pickle

sys.path.append(os.path.join("..", "common"))

from universe import Map

if __name__ == '__main__':
	##########
	# Load the config file
	##########
	seed = 98341
	options = {'base':'test_game'}

	# Create the base directory
	os.makedirs(options['base'])

	##########
	# Create a new universe from the config file
	##########

	UNIVERSE = Map(seed, options)

	map_location = os.path.join(options['base'], "Map.t0")

	f = open(map_location, 'w+')
	pickle.dump(UNIVERSE, f)

	##########
	# Create an empty player file
	##########

	from player import Player

	PLAYERS = {1:Player(1, (0,0), None), 2:Player(2, (0,0), None)}

	player_location = os.path.join(options['base'], "Players.t0")

	f = open(player_location, 'w+')
	pickle.dump(PLAYERS, f)

	##########
	# Create an empty Incoming queue
	##########

	IN_QUEUE = []

	incoming_location = os.path.join(options['base'], "Incoming.t0")

	f = open(incoming_location, 'w+')
	pickle.dump(IN_QUEUE, f)

	##########
	# Create an empty Outgoing queue
	##########

	OUT_QUEUE = []

	outgoing_location = os.path.join(options['base'], "Outgoing.t0")

	f = open(outgoing_location, 'w+')
	pickle.dump(OUT_QUEUE, f)

	########
	# Create the directories
	########

	os.mkdir(os.path.join(options['base'], "Incoming"))
	os.mkdir(os.path.join(options['base'], "Outgoing"))
	os.mkdir(os.path.join(options['base'], "New"))
	


	########
	# FIXME: Just using to test the server
	########
	from orders import Order

	orders = []
