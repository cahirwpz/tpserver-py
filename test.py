#!/usr/bin/env python

import sys, time
sys.path.append("Atlas-Python")
from atlas.transport.TCP.client import TcpClient
from atlas.transport.connection import args2address
import atlas

class Client(TcpClient):
	def setup(self):
		self.waiting = {}
		self.mode = "children"

	def ask(self, id):
		op = atlas.Operation("get", atlas.Object(id=id))
		self.send_operation(op)
		self.waiting[id] = 1
		
	def info_op(self, op):
		print op
		ent = op.arg
		if hasattr(ent, "id"):
			try:
				del self.waiting[ent.id]
			except:
				pass
			if hasattr(ent, self.mode):
				print ent.id, "---->",
				for id in getattr(ent, self.mode):
					print id,
					self.ask(id)
				print
				print "Still waiting on", self.waiting

	def error_op(self, op):
		obj = op.arg.op
		ent = obj.arg
		if hasattr(ent, "id"):
			print "Removing", ent.id
			try:
				del self.waiting[ent.id]
			except:
				pass
		print op
		print ent

	def loop(self):
		get = atlas.Operation("get")
		self.send_operation(get)

		obj = atlas.Object(id="demo", password="demo")
		login = atlas.Operation("login", obj)
		self.send_operation(login)
		self.waiting["demo"] = 1

		get = atlas.Operation("get")
		self.send_operation(get)

		self.ask("non_existant_id")
		self.ask("root")

		# Okay now ask for the base of the universe
		self.mode = "contains"
		
		while self.waiting:
			time.sleep(0.1)
			self.process_communication()

if __name__=="__main__":
	s = Client("Thousand Parsec Test Client", args2address(sys.argv))
	s.connect_and_negotiate()
	s.loop()
	
