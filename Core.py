import sys
import time
import os
import copy

import config

from atlas.transport.TCP import server
import atlas

# This is the "Global" bit, all clients talk through this main server.
class CoreServer(server.SocketServer):
	def setup(self):
		from atlas.transport.file import read_and_analyse

		self.definitions = read_and_analyse(os.path.join("data", "tp.bach"))
		self.startTime = time.time()

		# Load the accounts names into memory
		self.players = []

		from bits.ChatCore import ChatCore
		self.chatCore = ChatCore()

		print "Server ready"
	
	def idle(self):
		pass

	def authenticate(self, account, password):
		print len(self.players), config.maxPlayers
		if len(self.players) < config.maxPlayers:
			if account not in self.players:
				self.players.append(account)
				self.chatCore.add(account)
				return 1
		
		return 0

	def deauthenticate(self, account):
		self.chatCore.remove(account)
		self.players.remove(account)


# These exist for each client
class AnonymousClient(server.TcpClient):
	def get_op(self, op):
		""" Anonymous Get
			We send back
			   Version
			   Uptime
			   Number of Players
			   Max Number of Players
			   Admin Contact details
		"""
		# Check it's untargeted
		print (str(self.__class__) + ", %s") % "Got get Operation!"
		
		if hasattr(op, "arg") and hasattr(op.arg, "id"):
			print (str(self.__class__) + ", %s") % "Operation was targeted!"
			self.send_error(op, "Unauthenticated!")
		else:
			print (str(self.__class__) + ", %s") % "Returning Server stats"
			try:
				server_info = atlas.Object()
				server_info.Players = len(self.server.players)
				server_info.MaxPlayers = config.maxPlayers
				server_info.Uptime = time.time() - self.server.startTime
				server_info.Version = config.version
				server_info.AdminContact = config.adminContact
				
				self.reply_operation(op, atlas.Operation("info", server_info))
			except:
				from utils import do_traceback
				do_traceback()

	def login_op(self, op):
		print "Got a login operation"
		
		if not hasattr(op, "arg") or not hasattr(op.arg, "id") or not hasattr(op.arg, "password"):
			self.send_error(op, "No id or password")
			return
		
		account = op.arg.id
		password = op.arg.password
		
		if not self.server.authenticate(account, password):
			print (str(self.__class__) + ", %s") % "Client %s tried to authenticate with password %s" % (account, password)
			self.send_error(op, "The account doesn't exist or the password is wrong")
		else:
			print (str(self.__class__) + ", %s") % "Client %s authenticated successfully" % account
			
			# Okay lets upgrade ourselves to an authenticated Client
			self.__class__ = AuthenticatedClient
			self.__upgrade_init__(account)

			# Return an okay reply
			ent = atlas.Object(parents=["player"], id=account)
			self.reply_operation(op, atlas.Operation("info", ent, to=account))


# Anonymous Client's upgrade to these once the person has authenticated
class AuthenticatedClient(server.TcpClient, AnonymousClient):

	def login_op(self, op):
		self.send_error(op, "You are already logged in! Please logout first.")

	def __upgrade_init__(self, account):
		self.account = account

		# Need to load the "state" for this player

		# Connect the "state" to the chat server

	def __downgrade_init__(self):
		self.server.deauthenticate(self.account)
		
		# Save the "state" for this player

		# Clean up
		del self.account

	def __del__(self):
		print (str(self.__class__) + ", %s") % "Nuking"
		self.__downgrade_init__()
	
	def get_op(self, op):
		if hasattr(op, "arg"):
			
			if not hasattr(op.arg, "id"):
				# Untargeted Get
				print (str(self.__class__) + ", %s") % "Anonymous get"	
				AnonymousClient.get_op(self, op)
				
			else:
				id = op.arg.id

				if id == "root":
					# root is a special case, it should exist in all of the objects
					#
					# Because of this we return our own root which is combinded from
					# all the other roots.
					print (str(self.__class__) + ", %s") % "Getting the root object."
					
					root_obj = atlas.Object(id="root")

					# The children should come only from definitions
					root_obj.children = copy.deepcopy(self.server.definitions.get("root").children)

					# The root should contain all the stuff from the other roots
					#root_obj.contains = copy.deepcopy(self.server.definitions.get(""))

					self.reply_operation(op, atlas.Operation("info", root_obj))
					
				else:

					obj = None

					# Check definitions first
					if not obj:
						obj = self.server.definitions.get(id)
						
					# Then the chat server
					if not obj:
						obj = self.server.chatCore.get(id)

					# Then the players known Universe
					
					# Then the players designed
					
					# Then the players messages

					if obj:
						self.reply_operation(op, atlas.Operation("info", obj))
					else:
						self.send_error(op, "no object with id " + id)

				print (str(self.__class__) + ", %s") % "Targeted get " + id

	def logout_op(self, op):
		# Downgrade our selves to AnonymousClient
		self.__downgrade_init__()
		self.__class__ = AnonymousClient

	
