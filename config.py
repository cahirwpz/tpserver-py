
# Database config
host = "localhost"
user = "tp"
password = "tp-password"
database = "tp"

# Introduce artifical lag
lag = 0

# Add ruleset imports below here
import sobjects.Universe
import sobjects.Galaxy
import sobjects.System
import sobjects.Planet
import sobjects.Fleet

import sorders.NOp
#import sorders.Move
#import sorders.BuildFleet
#import sorders.SplitFleet
#import sorders.MergeFleet
