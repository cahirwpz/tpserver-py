
import atlas
import utils

class ChatCore:
	def __init__(self):
		self.root = {}
		self.root["root"] = atlas.Object(id="root")

		self.root.get("root").contains = []

		self.rooms = atlas.Object(id="rooms", parents=["ChatRoom"])
		self.rooms.contains = []
		
		self.root.get("root").contains.append( "rooms" )	
		self.root["rooms"] = self.rooms
		
		self.people = atlas.Object(id="people", parents=["ChatRoom"])
		self.people.contains = []

		self.root.get("root").contains.append( "people" )
		self.root["people"] = self.people
	
	def add(self, player):
		print "Adding"
		try:
			self.people.contains.append( player )
			self.root[ player ] = atlas.Object(id=player, parent=["ChatPlayer"])
		except:
			utils.do_traceback()

	def remove(self, player):

		for room in self.rooms.contains:
			room.contains.remove(player)

		# Remove person from the player list
		self.people.contains.remove(player)

		# remove the player
		del self.root[player]

	def get(self, id):
		return self.root.get(id)
