
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
			
			i = 0
			while i < len(room.contains):
				if room.contains[i] == player:
					del room.contains[i]

		# Remove person from the player list
		i = 0		
		while i < len(self.people.contains):
			if self.people.contains[i] == player:
				del self.people.contains[i]

		# remove the player

	def get(self, id):
		return self.root.get(id)
