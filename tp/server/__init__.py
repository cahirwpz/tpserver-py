"""\
Network Thousand Parsec server.
"""
# Python Import
import copy
import pickle
import time
import datetime
import socket

# Try to speed up things..
try:
	import psyco
except ImportError:
	pass

# Local imports
from version import version

import config
from config import dbconfig, dbecho, servername, serverip, metaserver

from tp import netlib
constants = netlib.objects.constants

# Base objects
from tp.server.bases.SQL       import NoSuch, PermissionDenied
from tp.server.bases.Board     import Board
from tp.server.bases.Category  import Category
from tp.server.bases.Component import Component
from tp.server.bases.Design    import Design
from tp.server.bases.Game      import Game, Lock, Event
from tp.server.bases.Message   import Message
from tp.server.bases.Object    import Object
from tp.server.bases.Order     import Order
from tp.server.bases.Property  import Property
from tp.server.bases.User      import User
from tp.server.bases.Resource  import Resource

# Database setup
from tp.server import db
db.setup(dbconfig, dbecho)
from sqlalchemy import *

class FullConnection(netlib.ServerConnection):
	def __init__(self, *args, **kw):
		netlib.ServerConnection.__init__(self, *args, **kw)
		self.user = None

	def user_get(self):
		return self.__user

	def user_set(self, value):
		if value is None:
			self.__user  = None
			self.game    = None		
			self.ruleset = None

		elif isinstance(value, User):
			self.__user  = value
			self.game    = value.playing
			self.ruleset = value.playing.ruleset
		else:
			raise TypeError("User value must either be None or a user object!")
	user = property(user_get, user_set)

	def check(self, packet):
		"""
		Checks if the user is logged in and the turns are not currently been processed.
		"""
		if self.user is None:
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_TEMP, 
							"You need to be logged in to use this functionality."))
			return False
	
		# Tell the database which game to examine	
		db.dbconn.use(db=self.game)

		# Check that the database isn't currently locked for turn processing
		if Lock.locked('processing'):
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_TEMP, 
								"Turn is currently been processed, please try again soon."))
			return False

		return True

	def _description_error(self, p):
		"""
		Orders/Objects which are describable are ruleset specific. 
		
		We deliberately don't register the Orders/Objects with the network
		library. Instead we catch them here and use the descriptions in the
		ruleset.
	
		This works because you need to logged in to access any of the
		describable functionality.
		"""
		if self.user is None:
			self._send(objects.Fail(p.sequence, constants.FAIL_TEMP, 
									"You must be logged in to use this functionality."))
			return True

		subtype = p._subtype

		# FIXME: Should check if this is an Order or Object
		if not (subtype in self.ruleset.ordermap):
			self._send(objects.Fail(p.sequence, constants.FAIL_FRAME, 
									"Packet doesn't match a type which I can describe."))
		else:
			print "The packet was described by ", self.ruleset.ordermap[subtype].packet(subtype)

			p.__process__(p._data, force=self.ruleset.ordermap[subtype].packet(subtype))
			del p._data

	def OnGetWithID(self, packet, type):
		"""\
		OnGetWithID(packet, type) -> [True | False]

		packet - Get packet to be processes, it must have the following
			packet.ids - The ids to be gotten
					
		type - The class used in processing, it must have the following
			type.realid(user, id)                - Get the real id for this object
			type(realid)                         - Creates the object
			typeinstance.to_packet(sequenceid)   - Creates a network packet with this sequence number
		"""
		if not self.check(packet):
			return True

		if len(packet.ids) != 1:
			self._send(netlib.objects.Sequence(packet.sequence, len(packet.ids)))

		for id in packet.ids:
			try:
				o = type(type.realid(self.user, id))
				self._send(o.to_packet(self.user, packet.sequence))

			except PermissionDenied:
				print "ERROR: No permission for %s with id %s." % (type, id)
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "No such %s." % type))
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

		key   = long(type.modified(self.user).strftime('%s'))
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
				self._send(o.to_packet(self.user, packet.sequence))

			except PermissionDenied:
				print "ERROR: No permission for %s with id %s." % (type, id)
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "No such %s." % type))
			except NoSuch:
				print "ERROR: No such %s with id %s, %s." % (type, id, slot)
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "No such order."))

		return True

	def OnGames_Get(self, p):
		ids = Game.ids()
		self._send(netlib.objects.Sequence(p.sequence, len(ids)))

		for id, time in ids:
			self._send(Game(id).to_packet(p.sequence))

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
		db.dbconn.use()
		
		if config.usercreation:
			try:
				username, game = User.split(packet.username)
			except TypeError, e:
				print e
				return self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_PERM, 
					"Did not specify which game you want to join.\nUsernames should be of the form <username>@<game>."))
			
			try:
				g = Game(shortname=game)
			except KeyError, e:
				print e
				return self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_PERM, 
					"The game you specified is not valid.\nUsernames should be of the form <username>@<game>."))

			# Check the username is not in use?
			pid = User.usernameid(g, username)
			if pid != -1:
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_PERM, "Username already in use, try a different name."))
				return True

			g.ruleset.player(username, packet.password, packet.email, packet.comment)

			self._send(netlib.objects.OK(packet.sequence, "User successfully created. You can login straight away now."))
			return True

		self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_TEMP, "Unable to create accounts at this time."))
		return True

	def OnLogin(self, packet):
		db.dbconn.use()

		try:
			username, game = User.split(packet.username)
		except TypeError, e:
			print e
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_PERM, 
				"Did not specify which game you want to join.\nUsernames should be of the form <username>@<game>."))
			return True

		try:
			g = Game(shortname=game)
		except KeyError, e:
			print e
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_PERM, 
				"The game you specified is not valid.\nUsernames should be of the form <username>@<game>."))
			return True

		pid = User.usernameid(g, username, packet.password)	
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
			self._send(object.to_packet(self.user, packet.sequence))

	def OnObject_GetID_ByContainer(self, packet):
		if not self.check(packet):
			return True
		
		objects = Object.byparent(packet.id)
#		self._send(netlib.objects.Sequence(packet.sequence,)

	def OnOrderDesc_GetID(self, packet):
		if not self.check(packet):
			return True

		# FIXME: There is a better place to put this class
		class OrderDesc(object):
			def modified(cls, user):
				return datetime.datetime.fromtimestamp(0)
			modified = classmethod(modified)
			
			def amount(cls, user):
				return len(user.playing.ruleset.ordermap.keys())
			amount = classmethod(amount)
			
			def ids(cls, user, start, amount):
				if amount== -1:
					amount = len(user.playing.ruleset.ordermap)
				return [(id, 0) for id in user.playing.ruleset.ordermap.keys()[start:amount]]
			ids = classmethod(ids)
		
			def id_packet(cls):
				return netlib.objects.OrderDesc_IDSequence
			id_packet = classmethod(id_packet)

		return self.OnGetID(packet, OrderDesc)	

	def OnOrderDesc_Get(self, packet):
		if not self.check(packet):
			return True

		self._send(netlib.objects.Sequence(packet.sequence, len(packet.ids)))

		mapping = self.user.playing.ruleset.ordermap
		for id in packet.ids:
			try:
				od = mapping[id].desc_packet(packet.sequence, id)
				self._send(od)
			except (KeyError, NoSuch):
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "No such order type."))

		return True

	def OnOrder_Get(self, packet):
		return self.OnGetWithIDandSlot(packet, Order, Object)

	def OnOrder_Insert(self, packet):
		if not self.check(packet):
			return True

		try:
			order = Order.from_packet(self.user, packet)
			
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

	def OnOrder_Probe(self, packet):
		if not self.check(packet):
			return True

		try:
			order = Order.from_packet(self.user, packet)
			
			# Are we allowed to do this?
			if not order.object.allowed(self.user):
				self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Permission denied."))
				print packet.id, packet.slot, "No Permission"
			else:	
				self._send(order.to_packet(self.user, packet.sequence))
		except NoSuch:
			print packet.id, packet.slot, "Probe failed."
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Order probe failed."))

		return True

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
			message = Message.from_packet(self.user, packet)
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
			design = Design.from_packet(self.user, packet)
			design.save()
			self._send(design.to_packet(self.user, packet.sequence))

		except PermissionDenied:
			print packet.id, "No Permission"
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Permission denied."))
		except NoSuch:
			print packet.id, "Adding failed."
			self._send(netlib.objects.Fail(packet.sequence, constants.FAIL_NOSUCH, "Design adding failed."))
		except ValueError:
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


import weakref
servers = weakref.WeakValueDictionary()

class FullServer(netlib.Server):
	# FIXME: Should start a thread for ZeroConf registration...
	handler = FullConnection
	debug = config.socketecho

	def __init__(self, *args, **kw):
		netlib.Server.__init__(self, *args, **kw)

		# Add us to the server list...
		servers[__builtins__['id'](self)] = self

		# Remove any order mapping from the network libray...
		netlib.objects.OrderDescs().clear()

		try:
			import signal

			# Make sure this thread gets these signals...
			signal.signal(signal.SIGTERM, self.shutdown)
			#signal.signal(signal.SIGKILL, self.exit)
			signal.signal(signal.SIGINT,  self.shutdown)
		except ImportError:
			print "Unable to set up UNIX signalling."

		# The thread for discovering this server
		from discover import DiscoverServer
		self.discover = DiscoverServer(metaserver)

		self.events = Event.latest()

		# Register all the games..
		self.locks  = []
		for id, time in Game.ids():
			self.gameadd(Game(id))

	def poll(self):
		# Get any new events..
		for event in Event.since(self.events):
			print 'New Event!!! -->', event

			if hasattr(self, event.eventtype):
				try:
					getattr(self, event.eventtype)(Game(event.game))
				except Exception, e:
					print e
			
			self.events = event.id

	def gameadd(self, g):
		already = [lock.game for lock in self.locks]
		if g.id in already:
			print "Got gameadd event for a game I already have a lock on!"
			return

		# Setup the game
		g.ruleset.setup()

		# Make the game discoverable	
		self.discover.GameAdd(g.to_discover())

		# Create a lock for this game
		db.dbconn.use(g)
		self.locks.append(Lock.new('serving'))

	def gameremove(self, g):
		pass

	def endofturn(self, game):
		# Send TimeRemaining Packets
		packet = netlib.objects.TimeRemaining(0, -1)

		for connection in self.connections.values():
			if isinstance(connection, FullConnection) and not connection.user is None:
				if connection.user.game != game.id:
					continue

				print "Sending EOT to", connection
				connection._send(packet)

	def shutdown(self, *args, **kw):
		# Remove the locks
		del self.locks

		# Close the discover threads
		self.discover.exit()
		
		# Exit this thread...
		import sys
		sys.exit()
	
	def serve_forever(self):
		# Start the discover threads..
		self.discover.start()

		# Need to wake up to check for things like EOT
		netlib.Server.serve_forever(self, 400)

