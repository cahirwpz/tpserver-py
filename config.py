
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
import db.MySQL as db
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
import sobjects.Universe
import sobjects.Galaxy
import sobjects.System
import sobjects.Planet
import sobjects.Fleet

import sorders.NOp
import sorders.Move
import sorders.BuildFleet
import sorders.SplitFleet
import sorders.MergeFleet
import sorders.Colonise

#import sactions.Move
import sactions.Clean
import sactions.FleetCombat
import sactions.Heal
import sactions.Win

# The order orders and actions occur
order = [sorders.BuildFleet,
		 sorders.SplitFleet,
		 sorders.MergeFleet,
		 sactions.Clean,
		 sorders.NOp,
		 sorders.Move, # sactions.Move, sorders.Move,
		 sactions.FleetCombat,
		 sactions.Clean,
		 sorders.Colonise,
		 sactions.Clean,
		 sactions.Heal,
		 sactions.Win,
		]
