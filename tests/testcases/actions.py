from test import TestCase, TestSuite

from logging import *
from tp.server.rules.base.actions.Combat import Fleet, Frigate, Battleship, Scout, Planet

class BaseBattleAction( TestCase ):
	""" """

	def runTest( self ):
		self.battle(
				Fleet( [ Frigate(), Battleship(), Scout(), Battleship(), Battleship(), Battleship() ]),
				Fleet( [ Battleship(), Battleship(), Planet() ] ))

	def display_hits( self, hits ):
		for ( hp, ship ) in hits:
			s = "Hit %s for %d" % ( ship.type, hp )

			if not ship.alive():
				s += "and destroyed it"

			debug( s )

	def battle( self, red, blue ):
		"""
		red and blue are the opposing sides, Fleet objects.
		"""
		round = 0

		while red.alive() and blue.alive():
			round += 1

			debug( "Round %d", round )

			red_hand = red.shake()

			debug( "* Red Fleet, %s", red_hand )

			blue_hand = blue.shake()

			debug( "* Blue Fleet, %s", blue_hand )

			if red_hand == blue_hand:
				debug( "* Draw" )
				blue_dmg = red.draw_damage()
				red_dmg = blue.draw_damage()

				if red_dmg:
					debug( "Blue Fleet does %d damage to Red Fleet", red_dmg )
					hits = red.hit(red_dmg)
					self.display_hits(hits)

				if blue_dmg:
					debug( "Red Fleet does %d damage to Blue Fleet", blue_dmg )
					hits = blue.hit(blue_dmg)
					self.display_hits(hits)

				continue

			if (red_hand, blue_hand) in (("Rock", "Scissors"), ("Scissors", "Paper"), ("Paper", "Rock")):
				debug( "* %s beats %s", red_hand, blue_hand )
				debug( "Red Fleet does %d damage to Blue Fleet", red.win_damage() )

				hits = blue.hit(red.win_damage())
				self.display_hits(hits)
			else:
				debug( "* %s beats %s", blue_hand, red_hand )
				debug( "Blue Fleet does %d damage to Red Fleet", blue.win_damage() )

				hits = red.hit(blue.win_damage())
				self.display_hits(hits)

		if red.alive():
			debug( "Red Fleet Wins" )
		elif blue.alive():
			debug( "Blue Fleet Wins" )
		else:
			debug( "Everybody died" )

		if red.running:
			debug( "Red Ran Away" )
		elif blue.running:
			debug( "Blue Ran Away" )

class RulesetActionTestSuite( TestSuite ):
	__name__  = 'RulesetActions'
	__tests__ = [ BaseBattleAction ]

__tests__ = [ RulesetActionTestSuite ]

