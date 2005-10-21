"""\
Heals a fleet to full health if they are orbiting a friendly planet.
"""

from turn import WalkUniverse

from sbases.Message import Message

def do(top):
	owners = {}
	def h(obj, owners=owners):
		if hasattr(obj, "owner") and obj.owner > 0:
			owners[obj.owner] = None

	WalkUniverse(top, "after", h)
	print "The following players still have objects in the universe", owners.keys()
	if len(owners.keys()) == 1:
		winner = owners.keys()[0]
		print "It seems that %i is the only player left so must be the winner!" % winner
		
		m = Message()
		m.bid = winner
		m.slot = -1
		m.subject = "Yay!"
		m.body = """\
<h1>You are the undisputed ruler of the universe!</h1>
You have crushed all your enemies and now only you remain.
It's a lonely place at the top but you'll live."""
		m.insert()

