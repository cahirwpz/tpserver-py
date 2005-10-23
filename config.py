
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
import tp.server.rules.base.orders.NOp
import tp.server.rules.base.orders.Move
import tp.server.rules.base.orders.SplitFleet
import tp.server.rules.base.orders.MergeFleet
import tp.server.rules.base.orders.Colonise
#import tp.server.rules.base.actions.Move
import tp.server.rules.base.actions.Clean
import tp.server.rules.base.actions.Win

import tp.server.rules.minisec.objects.Fleet
import tp.server.rules.minisec.orders.BuildFleet
import tp.server.rules.minisec.actions.FleetCombat
import tp.server.rules.minisec.actions.Heal

# The order orders and actions occur
order = [tp.server.rules.minisec.orders.BuildFleet,
		 tp.server.rules.base.orders.SplitFleet,
		 tp.server.rules.base.orders.MergeFleet,
		 tp.server.rules.base.actions.Clean,
		 tp.server.rules.base.orders.NOp,
		 tp.server.rules.base.orders.Move,
		 tp.server.rules.minisec.actions.FleetCombat,
		 tp.server.rules.base.orders.Colonise,
		 tp.server.rules.base.actions.Clean,
		 tp.server.rules.minisec.actions.Heal,
		 tp.server.rules.base.actions.Win,
		]
