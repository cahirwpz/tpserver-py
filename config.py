
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
lag = 0

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
#import sorders.MergeFleet
