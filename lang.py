

import struct

#"3 Component A AND (2 Component C OR 6 Component B)"
#
#2 Component C, 6 Component B, OR, 3 Component A, AND
#
#"0x1 0x2 0x3  Component C"
#"0x1 0x6 0x2  Component B"
#"0x4 0x0 0x0  OR"
#"0x1 0x3 0x1  Component A"
#"0x3 0x0 0x0  AND"

#   H   I   I

from config import db
import pickle

#connection = db.connect(config.host, config.user, config.password, config.database)
#string = connection.escape_string(data)
a = pickle.dumps(((1, 2, 3), (1, 6, 2), (4, 0, 0), (1, 3, 1), (3, 0, 0)))
print a
db.query("UPDATE component SET language='%(a)s' WHERE id = 4", a=a)

