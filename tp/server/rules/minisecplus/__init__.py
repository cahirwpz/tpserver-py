
import tp.server.rules.minisec import Ruleset as MinisecRuleset

class Ruleset(MinisecRuleset):
	"""
	Minisec+ Ruleset.

	This ruleset exploits extra features introduced (such as Designs) while
	still remaining as close to Minisec as possible.
	"""
	name = "Minisec+"
	version = "0.0.1"

	# The order orders and actions occur
	orderOfOrders = [
			BuildFleet, 		# Build all ships
			MergeFleet, 		# Merge fleets together
			SplitFleet, 		# Split any fleets - this means you can merge then split in one turn
			Clean, 				# Clean up fleets which no longer exist
			(Move, 'prepare'),  # Set the velocity of objects
			MoveAction, 		# Move all the objects about
			(Move, 'finalise'), # Check for objects which may have overshot the destination
			FleetCombat, 		# Perform a combat, ships may have escaped by moving away
			Colonise, 			# Colonise any planets, ships may have been destoryed or reached their destination
			Clean, 				# Remove all empty fleets
			Heal, 				# Repair any ships orbiting a friendly planet
			Win, 				# Figure out if there is any winner
			NOp, 				# NOp needs to occur last
	]

	def initalise(self):
		"""\
		Minisec 
		"""
		MinisecRuleset.initalise(self)

		# FIXME: Need to populate the database with the MiniSec properties,
		#  - Firepower
		#  - Armor/HP
		#  - Speed
		#  - Sensors (scouts ability to disappear)....
		pass


