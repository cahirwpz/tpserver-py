import sys
import time

import config

from atlas.transport.TCP import server
import atlas
#from atlas.transport.connection import args2address

# This is the "Global" bit, all clients talk through this main server.
class CoreServer(server.SocketServer):
	def setup(self):
		self.start_time = time.time()

		# Load the accounts names into memory
		self.Players = []
	
	def idle(self):
		pass

	def authenticate(self, account, password):
		print len(self.Players), config.MaxPlayers
		if len(self.Players) < config.MaxPlayers:
			if account not in self.Players:
				self.Players.append(account)
				return 1
		
		return 0

	def deauthenticate(self, account):
		self.Players.remove(account)


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
				server_info.Players = len(self.server.Players)
				server_info.MaxPlayers = config.MaxPlayers
				server_info.Uptime = time.time() - self.server.start_time
				server_info.Version = config.Version
				server_info.AdminContact = config.AdminContact
				
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
		# Check if it's an anonymous "get"
		if hasattr(op, "arg"):
			if not hasattr(op.arg, "id"):
				# Anonymous....
				print (str(self.__class__) + ", %s") % "Anonymous get"	
				AnonymousClient.get_op(self, op)
				pass
			else:
				# Targeted...
				print (str(self.__class__) + ", %s") % "Targeted get"
				pass

	def logout_op(self, op):
		# Downgrade our selves to AnonymousClient
		self.__downgrade_init__()
		self.__class__ = AnonymousClient

	
