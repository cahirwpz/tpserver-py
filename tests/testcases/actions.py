from test import TestCase, TestSuite

from tp.server.logging import msg
from tp.server.rules.base.actions.Combat import Fleet, Frigate, Battleship, Scout, Planet

class BaseBattleAction( TestCase ):
	""" """

	def run( self ):
		self.battle(
				Fleet( [ Frigate(), Battleship(), Scout(), Battleship(), Battleship(), Battleship() ]),
				Fleet( [ Battleship(), Battleship(), Planet() ] ))

		self.succeeded()

	def display_hits( self, hits ):
		for ( hp, ship ) in hits:
			s = "Hit %s for %d" % ( ship.type, hp )

			if not ship.alive():
				s += "and destroyed it"

			msg( s )

	def battle( self, red, blue ):
		"""
		red and blue are the opposing sides, Fleet objects.
		"""
		round = 0

		while red.alive() and blue.alive():
			round += 1

			msg( "Round %d" % round )

			red_hand = red.shake()

			msg( "* Red Fleet, %s" % red_hand )

			blue_hand = blue.shake()

			msg( "* Blue Fleet, %s" % blue_hand )

			if red_hand == blue_hand:
				msg( "* Draw" )
				blue_dmg = red.draw_damage()
				red_dmg = blue.draw_damage()

				if red_dmg:
					msg( "Blue Fleet does %d damage to Red Fleet" % red_dmg )
					hits = red.hit(red_dmg)
					self.display_hits(hits)

				if blue_dmg:
					msg( "Red Fleet does %d damage to Blue Fleet" % blue_dmg )
					hits = blue.hit(blue_dmg)
					self.display_hits(hits)

				continue

			if (red_hand, blue_hand) in (("Rock", "Scissors"), ("Scissors", "Paper"), ("Paper", "Rock")):
				msg( "* %s beats %s" % (red_hand, blue_hand) )
				msg( "Red Fleet does %d damage to Blue Fleet" % red.win_damage() )

				hits = blue.hit(red.win_damage())
				self.display_hits(hits)
			else:
				msg( "* %s beats %s" % (blue_hand, red_hand) )
				msg( "Blue Fleet does %d damage to Red Fleet" % blue.win_damage() )

				hits = red.hit(blue.win_damage())
				self.display_hits(hits)

		if red.alive():
			msg( "Red Fleet Wins" )
		elif blue.alive():
			msg( "Blue Fleet Wins" )
		else:
			msg( "Everybody died" )

		if red.running:
			msg( "Red Ran Away" )
		elif blue.running:
			msg( "Blue Ran Away" )

class RulesetActionTestSuite( TestSuite ):
	__name__ = 'RulesetActions'

	def __init__( self ):
		TestSuite.__init__( self )

		self.addTest( BaseBattleAction )

__tests__ = [ RulesetActionTestSuite ]

