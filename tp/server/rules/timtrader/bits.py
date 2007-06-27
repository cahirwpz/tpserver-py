"""
This file reads in the prodcom.csv file and figures out all the
resource types that exist. It also warns if there are any resources
which have no producers.
"""

import csv
import os

class Resource(object):
	def __init__(self, amount, name):
		self.amount = amount
		self.name   = name

	def __and__(self, other):
		return And_(self, other)

	def __or__(self, other):
		return Or_(self, other)

	def __str__(self):
		return "<%s %s>" % (self.amount, self.name)

	def components(self):
		return [self.name,]

class Compound(object):
	type = 'UNKNOWN'
	def __init__(self, left, right):
		self.left  = left
		self.right = right
	
	def __str__(self):
		return "%s %s %s" % (self.left, self.type, self.right)

	def __and__(self, other):
		return And_(self, other)

	def __or__(self, other):
		return Or_(self, other)

	def components(self):
		return self.left.components()+self.right.components()

class And_(Compound):
	type = 'AND'

class Or_(Compound):
	type = 'OR'

def split(s):
	r = None
	if s.find(' and ') != -1:
		bits = s.split(' and ')
		
		r = split(bits[0])
		for bit in bits[1:]:
			r = r & split(bit)
	elif s.find(' or ') != -1:
		bits = s.split(' or ')
	
		r = split(bits[0])
		for bit in bits[1:]:
			r = r | split(bit)
	elif len(s) > 0:
		amount, name = s.split(' ', 1)
		r = Resource(amount, name)

	return r

reader = csv.DictReader(open(os.path.join("other", "prodcon.csv"), "r"))

resources = set()
resources_producedby = {}
resources_usedby     = {}

fn = ''
for row in reader:
	fn = (row['Factory Name'], fn)[len(row['Factory Name']) == 0]

	if fn == row['Factory Name']:
		print
		print fn
		print row['Description']

	requirement = split(row['Requirement'])	
	produce     = split(row['Produce'])	

	print "\t\t %s%s-> %s" % (requirement, (4-(len(str(requirement))+1)/8)*'\t', produce)
	if requirement != None:
		resources.update(requirement.components())

		for resource in requirement.components():
			if not resources_usedby.has_key(resource):
				resources_usedby[resource] = set()
			resources_usedby[resource].add(fn)
	if produce != None:
		resources.update(produce.components())

		for resource in produce.components():
			if not resources_producedby.has_key(resource):
				resources_producedby[resource] = set()
			resources_producedby[resource].add(fn)

for resource in resources:
	print resource

	print "Produced By:",
	if resources_producedby.has_key(resource):
		print tuple(resources_producedby[resource])
	else:
		print "**WARNING** Not produced by anything."
	print "Used By:    ",
	if resources_usedby.has_key(resource):
 		print tuple(resources_usedby[resource])
	else:
		print "**WARNING** Not used by anything."
	print

