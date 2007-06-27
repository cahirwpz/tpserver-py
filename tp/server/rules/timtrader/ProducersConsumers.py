"""
This file reads in the prodcom.csv file and figures out all the
resource types that exist. It also warns if there are any goods
which have no producers.
"""

import csv
import os

class Good(object):
	def __init__(self, amount, name):
		self.amount = amount
		self.name   = name.title()

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

class Factory(object):
	def __init__(self, name, desc, maximum=-1):
		self.name = name
		self.desc = desc
		self.max  = max	

		self.products = []

	def add(self, requirements, produce):
		self.products.append(requirements, produce)

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
		r = Good(float(amount), name)

	return r

def loadfile():
	"""
	loadfile -> factories, goods
	"""
	reader = csv.DictReader(open(os.path.join("other", "prodcon.csv"), "r"))

	factories = []

	factory = None
	for row in reader:
		if factory is None or factory.name != row['Factory Name']:
			factory = Factory(row['Factory Name'], row['Description'], row['Maximum'])
			factories.append(factory)

		requirement = split(row['Requirement'])	
		produce     = split(row['Produce'])	

		factory.add(requirement, produce)

	return factories

if __name__ == "__main__":
	reader = csv.DictReader(open(os.path.join("other", "prodcon.csv"), "r"))

	goods = set()
	goods_producedby = {}
	goods_usedby     = {}

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
			goods.update(requirement.components())

			for resource in requirement.components():
				if not goods_usedby.has_key(resource):
					goods_usedby[resource] = set()
				goods_usedby[resource].add(fn)
		if produce != None:
			goods.update(produce.components())

			for resource in produce.components():
				if not goods_producedby.has_key(resource):
					goods_producedby[resource] = set()
				goods_producedby[resource].add(fn)

	# Compare goods against the resource.csv file...
	reader = csv.DictReader(open(os.path.join("other", "resources.csv"), "r"))
	resources = set()
	for row in reader:
		resources.add(row['namesingular'])

	inresource = resources - goods
	ingood     = goods - resources

	if len(inresource) > 0:
		print "These goods are not used in ProdCon.csv file"
		print tuple(inresource)
		print

	if len(ingood) > 0:
		print "***WARNING*** These goods are not defined in resources.csv!"
		print tuple(ingood)
		print

	for resource in goods:
		print resource

		print "Produced By:",
		if goods_producedby.has_key(resource):
			print tuple(goods_producedby[resource])
		else:
			print "**WARNING** Not produced by anything."
		print "Used By:    ",
		if goods_usedby.has_key(resource):
			print tuple(goods_usedby[resource])
		else:
			print "**WARNING** Not used by anything."
		print

