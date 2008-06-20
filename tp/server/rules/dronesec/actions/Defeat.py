"""\
This action sends the a message to defeated players.
"""

from tp.server.bases.Message import Message
from tp.server.utils import WalkUniverse

def do(top):
	owners = {}
	overlords = {}
	def h(obj, owners=owners, overlords = overlords):
		if hasattr(obj, "owner") and obj.owner > 0:
			if not owners.has_key(obj.owner):
				owners[obj.owner] = 0
			owners[obj.owner] += 1
			if obj.type.endswith('overlord.Fleet'):
				overlords[obj.owner] = obj

	WalkUniverse(top, "after", h)
	for player, num in owners.items():
		if num == 1:
			print "It seems that %i has only his overlord left. Player Defeated" % player

			m = Message()
			m.bid = player
			m.slot = -1
			m.subject = "Yay!"
			m.body = """\
<h1>You have been Defeated!</h1>
Your home planet and fleets have been eliminated
All that is left is one lonely overlord which finishes himself off"""
			m.insert()
			overlords[player].remove()
