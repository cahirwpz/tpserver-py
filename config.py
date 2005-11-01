
try:
	import psyco
except ImportError:
	pass
	
try:
	from tp import netlib
except ImportError:
	import sys
	sys.path.append("../")
	from tp import netlib

import sys
sys.path.append(".")

class config:
	pass

# Database config
import tp.server.db.MySQL as db
db = db
dbconfig = config()
dbconfig.host = "localhost"
dbconfig.user = "tp"
dbconfig.password = "tp-password"
dbconfig.database = "tp"
db.connect(dbconfig)

# Introduce artifical lag
lag = 1

# Admin users
admin = (1,)

# Add ruleset imports below here

# Generic
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
		 Move,
		 MoveAction,
		 Move,
		 FleetCombat,
		 Colonise,
		 Clean,
		 Heal,
		 Win,
		]
