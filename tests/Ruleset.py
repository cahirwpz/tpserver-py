
ruleset = None
def setup_module(self):
	import os
	try:
		module = os.environ['TEST_RULESET']
	except KeyError:
		raise Exception("You need to specify the TEST_RULESET environment varible!")

	global ruleset
	ruleset = os.environ['TEST_RULESET']

	# FIXME: Check that no database currently exists!

# FIXME: Do I need to do this?
import sys
sys.path.insert(0, '.')

from tp.server.bases.Game import Game

gamename = 'Thousand Parsec Testing Game'
class TestRuleset1(object):
	"""
	This test does some rudimentary tests to make sure a ruleset has some basic
	functionality.
	"""

	def test_load(self):
		"""
		Tests that a ruleset can be successfully loaded.
		"""
		g = Game()
		g.ruleset  = ruleset

	def test_setup(self):
		"""
		Tests that a ruleset's 'setup' method works.

		Also makes sure the 'ordermap' attribute is not empty.
		"""

	def test_initialise(self):
		"""
		Tests that we can initialise a new game using the ruleset.
		"""
		# Okay create a new game then
		g = Game()
		g.ruleset  = ruleset
		g.shortname= self.__class__.__name__
		g.longname = gamename
		g.admin    = 'admin@localhost'
		g.comment  = 'A test game'
		g.turn     = 0
		g.commandline="Unknown!"
		g.save()

		g.ruleset.initialise()

class TestRuleset2(object):
	"""
	This test does some rudimentary tests to make sure a ruleset has some basic
	functionality.
	"""
	def setup_class(cls):
		# Okay create a new game then
		print 'Class name!', cls.__name__

		g = Game()
		g.ruleset  = ruleset
		g.shortname= cls.__name__
		g.longname = cls.__name__
		g.admin    = 'admin@localhost'
		g.comment  = 'A test game'
		g.turn     = 0
		g.commandline="Unknown!"
		g.save()

		g.ruleset.initialise()

	def test_player(self):
		"""
		Tests that the ruleset can add a player.
		"""
		ln = self.__class__.__name__
		r = Game(shortname=ln).ruleset
		r.player('testplayer1', 'password', 'email', 'comment')	

	def test_turn(self):
		"""
		Test that the ruleset turn method runs..
		"""
		ln = self.__class__.__name__
		r = Game(shortname=ln).ruleset
		r.turn()
	
	def test_update(self):
		"""
		Tests that the ruleset update method runs..
		"""
		ln = self.__class__.__name__
		r = Game(shortname=ln).ruleset
		r.update()
