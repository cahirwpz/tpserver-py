
try:
	import psyco
except ImportError:
	pass
	
# Database config
dbconfig = "mysql://tp:tp-password@localhost/tp"
#dbconfig = "sqlite:///tp.db"

# Introduce artifical lag
lag = 1

# Admin users
admin = (1,)

usercreation = True
games = ('tp',)

# Add ruleset imports below here
# -------------------------------------------------------------
# Generic
import tp.server.rules.minisec as ruleset

import tp.server.rules.base.objects.Universe
import tp.server.rules.base.objects.Galaxy
import tp.server.rules.base.objects.System
import tp.server.rules.base.objects.Planet

import tp.server.rules.minisec.objects.Fleet

import tp.server.rules.base.orders.NOp as NOp
import tp.server.rules.base.orders.MergeFleet as MergeFleet
import tp.server.rules.base.orders.Colonise as Colonise
import tp.server.rules.base.actions.Move as MoveAction
import tp.server.rules.base.actions.Clean as Clean
import tp.server.rules.base.actions.Win as Win

# Minisec specific imports
import tp.server.rules.minisec.orders.Move as Move
import tp.server.rules.minisec.orders.BuildFleet as BuildFleet
import tp.server.rules.minisec.orders.SplitFleet as SplitFleet
import tp.server.rules.minisec.actions.FleetCombat as FleetCombat
import tp.server.rules.minisec.actions.Heal as Heal

# The order orders and actions occur
order = [BuildFleet,
		 SplitFleet,
		 MergeFleet,
		 Clean,
		 NOp,
		 (Move, 'prepare'),
		 MoveAction,
		 (Move, 'finalise'),
		 FleetCombat,
		 Colonise,
		 Clean,
		 Heal,
		 Win,
		]

