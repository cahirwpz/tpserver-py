"""\
Network Thousand Parsec server.
"""
# Python Import
import copy
import pickle
import time
import socket

# Try to speed up things..
try:
	import psyco
except ImportError:
	pass

# Local imports
import config
from config import dbconfig


from tp import netlib
constants = netlib.objects.constants

# Base objects
from tp.server.bases.SQL       import NoSuch
from tp.server.bases.Board     import Board
from tp.server.bases.Category  import Category
from tp.server.bases.Component import Component
from tp.server.bases.Design    import Design
from tp.server.bases.Message   import Message
from tp.server.bases.Object    import Object
from tp.server.bases.Order     import Order
from tp.server.bases.Property  import Property
from tp.server.bases.User      import User
from tp.server.bases.Resource  import Resource

# Database setup
from sqlalchemy import *
from tp.server import db
db.setup(dbconfig)

class FullConnection(netlib.ServerConnection):
	def __init__(self, *args, **kw):
		netlib.ServerConnection.__init__(self, *args, **kw)
		self.user = None

	def check(self, packet):
		"""
		Checks if the user is logged in and the turns are not currently been processed.
		"""
		if self.user == None:
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_TEMP, 
							"You need to be logged in to use this functionality."))
			return False

		# Reset the database connection
		db.dbconn.use(db=self.user.domain())

		# Check that the database isn't currently locked for turn processing
#		result = db.query("SELECT COUNT(type) FROM `lock` WHERE type = 'turn'")
#		if len(result) > 0:
#			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_TEMP, 
#								"Turns are currently been processed, please try again soon."))
#			return False

		return True

	def OnGetWithID(self, packet, type):
		"""\
		OnGetWithID(packet, type) -> [True | False]

		packet - Get packet to be processes, it must have the following
			packet.ids - The ids to be gotten
					
		type - The class used in processing, it must have the following
			type.realid(user, id)                - Get the real id for this object
			type(realid)                         - Creates the object
			typeinstance.allowed(user)           - Is the user allowed to see this object
			typeinstance.protect(user)           - Protect the object against this user
			typeinstance.to_packet(sequenceid)   - Creates a network packet with this sequence number
		"""
		if not self.check(packet):
			return True

		print "Getting stuff with ids", packet.ids
		
		if len(packet.ids) != 1:
			self._send(netlib.objects.Sequence(packet.sequence, len(packet.ids)))

		for id in packet.ids:
			try:
				# Get the real id of the object
				id = type.realid(self.user, id)
				
				o = type(id)

				# Is the user allowed to access this object?
				if not o.allowed(self.user):
					print "ERROR: No permission for %s with id %s." % (type, id)
					self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "No such %s." % type))
				else:
					# Protect certain details from a user (ie if can see only some of the object)
					o = o.protect(self.user)
					self._send(o.to_packet(packet.sequence))

			except NoSuch:
				print "ERROR: No such %s with id %s." % (type, id)
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "No such %s." % type))

		return True
	
	def OnGetID(self, packet, type):
		"""\
		OnGethID(packet, type) -> [True | False]

		packet - Get packet to be processes, it must have the following
			packet.key    - The last modified time
			packet.start  - Index to start from
			packet.amount - The number of items to get
					
		type - The class used in processing, it must have the following
			type.modified(user)                 - Get the latest modified time for that type (that this user can see)
			type.amount(user)                   - Get the number of this that exist (that this user can see)
			type.ids(user, start, amount)       - Get the ids (that this user can see)
			type.ids_packet()                   - Get the packet type for sending a list of ids
		"""
		if not self.check(packet):
			return True

		print "Getting IDs with ", packet.key, packet.start, packet.amount

		key = type.modified(self.user)
		total = type.amount(self.user)
		
		if packet.key != -1 and key != packet.key:
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Key %s is no longer valid, please get a new key." % (packet.key,)))
			return True
		
		if packet.start+packet.amount > total:
			print "Requested %s %s Actually %s." % (packet.start, packet.amount, total)
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Requested to many IDs. (Requested %s, Actually %s." % (packet.start+packet.amount, total)))
			return True

		if packet.amount == -1:
			left = 0
		else:
			left = total - (packet.start+packet.amount)
		
		ids = type.ids(self.user, packet.start, packet.amount)
		self._send(type.id_packet()(packet.sequence, key, left, ids))

		return True
	
	def OnGetWithIDandSlot(self, packet, type, container):
		"""\
		OnGetWithIDandSlot(packet, type, container) -> [True | False]

		packet - Get packet to be processes, it must have the following
			packet.id		- The id of the container
			packet.slots	- The slots to be gotten
					
		type - The class used in processing, it must have the following
			type(realid, slot)                   - Creates the object
			typeinstance.allowed(user)           - Is the user allowed to see this object
			typeinstance.protect(user)           - Protect the object against this user
			typeinstance.to_packet(sequenceid)   - Creates a network packet with this sequence number

		container - The class that contains the other class
			container.realid(user, id)           - Get the real id for the container object
		"""
		if not self.check(packet):
			return True
		
		# Get the real id
		id = container.realid(self.user, packet.id)
		
		if len(packet.slots) != 1:
			self._send(netlib.objects.Sequence(packet.sequence, len(packet.slots)))
		for slot in packet.slots:
			try:
				o = type(id, slot)

				# Is the user allowed to access this object?
				if not o.allowed(self.user):
					print "ERROR: No permission for %s with id %s." % (type, id)
					self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "No such %s." % type))
				else:
					# Protect certain details from a user (ie if can see only some of the object)
					o = o.protect(self.user)
					self._send(o.to_packet(packet.sequence))

			except NoSuch:
				print "ERROR: No such %s with id %s, %s." % (type, id, slot)
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "No such order."))

		return True

	def OnFeature_Get(self, p):
		self._send(netlib.objects.Feature(p.sequence, [ \
			constants.FEATURE_HTTP_THIS,
			constants.FEATURE_KEEPALIVE,
			constants.FEATURE_ORDERED_OBJECT,
			constants.FEATURE_ORDERED_ORDERDESC,
			constants.FEATURE_ORDERED_BOARD,
			constants.FEATURE_ORDERED_CATEGORY,
			constants.FEATURE_ORDERED_DESIGN,
			constants.FEATURE_ORDERED_COMPONENT,
			constants.FEATURE_ORDERED_PROPERTY,
			constants.FEATURE_ORDERED_RESOURCE,
			constants.FEATURE_ACCOUNT_REGISTER,
		]))
		return True

	def OnAccount(self, packet):
		#db.query("USE tp")
		
		if config.usercreation:
			username = packet.username
			if username.find('@') == -1:
				#return self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_PERM, 
				#	"Did not specify which game you want to join.\nUsernames should be of the form <username>@<game>."))
				username += "@tp"
			
			# FIXME: Need to check that the game is a valid game..
			userpart, game = username.split('@', 1)
			if not game in config.games:
				return self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_PERM, 
					"The game you specified is not valid.\nUsernames should be of the form <username>@<game>."))

			# Check the username is not in use?
			pid = User.usernameid(username)
			if pid != -1:
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_PERM, "Username already in use, try a different name."))
				return True

			account = User(None, packet)
			account.username = username
			account.save()
			config.ruleset.spawn_player(account)
			self._send(netlib.objects.OK(packet.sequence, "User successfully created. You can login straight away now."))
			return True

		self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_TEMP, "Unable to create accounts at this time."))
		return True

	def OnLogin(self, packet):
		# We need username and password
		pid = User.usernameid(packet.username, packet.password)
	
		if pid == -1:
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Login incorrect or unknown username!"))
		else:
			self.user = User(id=pid)
			self._send(netlib.objects.OK(packet.sequence, "Login Ok!"))
			
		return True

	def OnObject_GetById(self, packet):
		# FIXME: This should show the correct number of orders for a certain person
		return self.OnGetWithID(packet, Object)
		
	def OnObject_GetID(self, packet):
		return self.OnGetID(packet, Object)	

	def OnObject_GetID_ByPos(self, packet):
		if not self.check(packet):
			return True

		objects = Object.bypos(packet.pos, packet.size)

		self._send(netlib.objects.Sequence(packet.sequence, len(objects)))

		for object in objects:
			self._send(object.to_packet(packet.sequence))

	def OnObject_GetID_ByContainer(self, packet):
		if not self.check(packet):
			return True
		
		objects = Object.byparent(packet.id)
#		self._send(netlib.objects.Sequence(packet.sequence,)

	def OnOrderDesc_GetID(self, packet):
		if not self.check(packet):
			return True

		# FIXME: There is a better place to put this class
		class OrderDesc:
			def modified(cls, user):
				return 0
			modified = classmethod(modified)
			
			def amount(cls, user):
				return len(Order.types.keys())
			amount = classmethod(amount)
			
			def ids(cls, user, start, amount):
				return [(id, 0) for id in Order.types.keys()[start:amount]]
			ids = classmethod(ids)
		
			def id_packet(cls):
				return netlib.objects.OrderDesc_IDSequence
			id_packet = classmethod(id_packet)

		return self.OnGetID(packet, OrderDesc)	

	def OnOrderDesc_Get(self, packet):
		if not self.check(packet):
			return True

		self._send(netlib.objects.Sequence(packet.sequence, len(packet.ids)))

		for id in packet.ids:
			try:
				self._send(Order.desc_packet(packet.sequence, id))
			except NoSuch:
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "No such order type."))

		return True

	def OnOrder_Get(self, packet):
		return self.OnGetWithIDandSlot(packet, Order, Object)

	def OnOrder_Insert(self, packet):
		if not self.check(packet):
			return True

		try:
			order = Order(packet=packet)
			
			# Are we allowed to do this?
			if not order.object.allowed(self.user):
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Permission denied."))
				print packet.id, packet.slot, "No Permission"
			else:	
				order.insert()
				self._send(netlib.objects.OK(packet.sequence, "Order added."))
		except NoSuch:
			print packet.id, packet.slot, "Adding failed."
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Order adding failed."))

		return True
	OnOrder = OnOrder_Insert

	def OnOrder_Remove(self, packet):
		if not self.check(packet):
			return True

		self._send(netlib.objects.Sequence(packet.sequence, len(packet.slots)))

		for slot in packet.slots:
			try:
				order = Order(packet.id, slot)
				
				# Are we allowed to do this?
				if not order.object.allowed(self.user):
					self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "No such order."))
					print self.user.id, packet.id, slot, "No Permission"
				else:	
					order.remove()
					self._send(netlib.objects.OK(packet.sequence, "Order removed."))
			except NoSuch:
				print packet.id, slot, "No such order."
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "No such order."))

		return True

	def OnBoard_Get(self, packet):
		return self.OnGetWithID(packet, Board)
		
	def OnBoard_GetID(self, packet):
		return self.OnGetID(packet, Board)	
	
	def OnMessage_Get(self, packet):
		return self.OnGetWithIDandSlot(packet, Message, Board)

	def OnMessage_Insert(self, packet):
		if not self.check(packet):
			return True

		try:
			# Mangle the board id
			packet.id = Board.mangleid(packet.id, self.user.id)

			message = Message(packet=packet)
			message.insert()
			self._send(netlib.objects.OK(packet.sequence, "Message added."))
		except NoSuch:
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Message adding failed."))

		return True

	OnMessage = OnMessage_Insert

	def OnMessage_Remove(self, packet):
		if not self.check(packet):
			return True

		self._send(netlib.objects.Sequence(packet.sequence, len(packet.slots)))

		for slot in packet.slots:
			try:
				message = Message(Board.realid(self.user, packet.id), slot)
				message.remove()
				self._send(netlib.objects.OK(packet.sequence, "Message removed."))
			except NoSuch:
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "No such message."))

		return True

	def OnResource_Get(self, packet):
		return self.OnGetWithID(packet, Resource)
		
	def OnResource_GetID(self, packet):
		return self.OnGetID(packet, Resource)

	def OnCategory_Get(self, packet):
		return self.OnGetWithID(packet, Category)

	def OnCategory_GetID(self, packet):
		return self.OnGetID(packet, Category)

	def OnComponent_Get(self, packet):
		return self.OnGetWithID(packet, Component)

	def OnComponent_GetID(self, packet):
		return self.OnGetID(packet, Component)

	def OnDesign_Get(self, packet):
		return self.OnGetWithID(packet, Design)

	def OnDesign_GetID(self, packet):
		return self.OnGetID(packet, Design)

	def OnDesign_Add(self, packet):
		if not self.check(packet):
			return True

		try:
			design = Design(packet=packet)
			
			# Are we allowed to do this?
			if not design.allowed(self.user):
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Permission denied."))
				print packet.id, "No Permission"
			else:	
				design.save()
				self._send(design.to_packet(packet.sequence))
		except ValueError:
			print packet.id, "Adding failed."
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Design adding failed."))
			
		except NoSuch:
			print packet.id, "Adding failed."
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Design adding failed."))

		return True
	OnDesign = OnDesign_Add

	def OnProperty_Get(self, packet):
		return self.OnGetWithID(packet, Property)

	def OnProperty_GetID(self, packet):
		return self.OnGetID(packet, Property)

	def OnPlayer_Get(self, packet):
		return self.OnGetWithID(packet, User)

	def _send(self, *args, **kw):
		return netlib.ServerConnection._send(self, *args, **kw)

class FullServer(netlib.Server):
	# FIXME: Should start a thread for checking the database for locks...
	# FIXME: Should start a thread for ZeroConf registration...
	handler = FullConnection
	debug = True

	def __init__(self, *args, **kw):
		netlib.Server.__init__(self, *args, **kw)

		# Load all the order descriptions and print them out.
		Order.load_all()
		for key, value in netlib.objects.OrderDescs().items():
			print key, value
			print value.names
		

	def endofturn(self, sig, frame):
		packet = netlib.objects.TimeRemaining(0, 0)
		for connection in self.connections:
			connection._send(packet)

def main():
	port = 6923
	while True:
		try:
			s = FullServer("", port, port+1)
			print "Used port", port
		except socket.error, e:
			print e, "This port in use...", port
			port += 1
			continue
		
		try:
			import signal

			signal.signal(signal.SIGUSR1, s.endofturn)
		except ImportError:
			print "Unable to set up UNIX signalling, SIGUSR1 will not cause turn generation!"

		# Import all the order_desc from the database
		Order.load_all()
		for key, value in netlib.objects.OrderDescs().items():
			print key, value
			print value.names

		s.serve_forever()

if __name__ == "__main__":
	main()

