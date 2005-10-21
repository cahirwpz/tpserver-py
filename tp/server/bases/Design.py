
from config import db, netlib

from SQL import *
from Component import Component
from Property import Property

import pyscheme as scheme

class Design(SQLBase):
	tablename = "`design`"
	tablename_category = "`design_category`"
	tablename_component = "`design_component`"

	def categories(self):
		"""\
		categories() -> [id, ...]

		Returns the categories the design is in.
		"""
		results = db.query("""SELECT category FROM %(tablename_category)s WHERE %(tablename)s=%(id)s""", 
			tablename_category=self.tablename_category, tablename=self.tablename, id=self.id)
		return [x['category'] for x in results]

	def components(self):
		"""\
		components() -> [id, ...]

		Returns the components the design contains.
		"""
		results = db.query("""SELECT component, amount FROM %(tablename_component)s WHERE %(tablename)s=%(id)s""", 
			tablename_component=self.tablename_component, tablename=self.tablename, id=self.id)
		return [(x['component'], x['amount']) for x in results]

	def used(self):
		"""\
		used() -> value

		Returns the properties (and values) a design has.
		"""
		# Need to check if the design is valid
		if not self.check()[0]:
			return -1
		
		# FIXME: This is a bit of a hack (and most probably won't work on non-MySQL)
		results = db.query("""SELECT SUM(value) AS inplay FROM object_extra WHERE name = 'ships' AND `key` = '%(key)s'""", key=repr(self.id))
		try:
			inplay = long(results[0]['inplay'])
		except (KeyError, ValueError):
			inplay = 0
	
		results = db.query("""SELECT SUM(value) as beingbuilt FROM order_extra JOIN `order` ON order.id = order_extra.order WHERE name = 'ships' AND type = 'sorders.Build' AND `key` = '%(key)s'""", key=repr(self.id))
		try:
			beingbuilt = long(results[0]['beingbuilt'])
		except (KeyError, ValueError):
			beingbuilt = 0
		
		return inplay+beingbuilt

	def rank(self):
		# FIXME: This is a hack, there should be a better way to do this
		results = db.query("""SELECT DISTINCT cp.property AS id, p.rank AS rank FROM component_property AS cp JOIN property AS p ON p.id = cp.property WHERE cp.component in %s ORDER by rank""" 
			% str(zip(*self.components())[0]).replace('L','').replace(',)',')'))

		ranks = {}
		for result in results:
			rank, id = result['rank'], result['id']
		
			if not ranks.has_key(rank):
				ranks[rank] = []
			ranks[rank].append(id)

		return ranks

	def calculate(self):
		"""\
		calculate() -> Interpretor, Design

		Calculates all the properties on a design. 
		Returns the Interpretor (used to create the design and the actual design).
		"""
		i = scheme.make_interpreter()

		# Step 1 -------------------------------------

		ranks = self.rank()
		print "The order I need to calculate stuff in is,", ranks

		# Step 2 -------------------------------------

		# The design object
		class Design(dict):
			pass

		design = Design()
		scheme.environment.defineVariable(scheme.symbol.Symbol('design'), design, i.get_environment())

		# Step 3 -------------------------------------
		for rank in ranks.keys():
			for property_id in ranks[rank]:
				property = Property(property_id)

				# Where we will store the values as calculated
				bits = []
		
				# Get all the components we contain
				for component_id, amount in self.components():
					# Create the component object
					component = Component(component_id)

					# Calculate the actual value for this design
					value = component.property(property_id)
					if value:
						print "Now evaluating",
						print value
						value = i.eval(scheme.parse("""( %s design)""" % value))

						print "The value calculated for component %i was %r" % (component_id, value)
					
						for x in range(0, amount):
							bits.append(value)

				print "All the values calculated where", bits
				bits_scheme = "(list"
				for bit in bits:
					bits_scheme += " " + str(bit).replace('L', '')
				bits_scheme += ")"
				print "In scheme that is", bits_scheme
				
				total = i.eval(scheme.parse("""(let ((bits %s)) (%s design bits))""" % (bits_scheme, property.calculate)))
				value, display = scheme.pair.car(total), scheme.pair.cdr(total)

				print "In total I got '%i' which will be displayed as '%s'" % (value, display)
				design[property.name] = (property_id, display)

				def t(design, name=property.name):
					return design[name][1]
				
				i.install_function('designtype.'+property.name, t)
				
		print "The final properties we have are", design.items()
		return i, design, rank
	
	def check(self):
		"""\
		check() -> Interpretor, Design

		Checks the requirements of a design.
		"""
		# Step 1, calculate the properties
		i, design, rank = self.calculate()
		
		total_okay = True
		total_feedback = []

		# Step 2, calculate the requirements for the properties
		ranks = self.rank()
		for rank in ranks.keys():
			for property_id in ranks[rank]:

				property = Property(property_id)
				if property.requirements == '':
					print "Property with id (%i) doesn't have any requirements" % property_id
					continue
			
				print "Now checking the following requirement"
				print property.requirements
				result = i.eval(scheme.parse("""(%s design)""" % property.requirements))
				print "Result was:", result
				okay, feedback = scheme.pair.car(result), scheme.pair.cdr(result)

				if okay != scheme.symbol.Symbol('#t'):
					total_okay = False
		
				if feedback != "":
					total_feedback.append(feedback)

				
		# Step 3, calculate the requirements for the components
		for component_id, amount in self.components():
			component = Component(component_id)
			if component.requirements == '':
				print "Component with id (%i) doesn't have any requirements" % property_id
				continue
			
			print "Now checking the following requirement"
			print component.requirements
			result = i.eval(scheme.parse("""(%s design)""" % component.requirements))
			print "Result was:", result
			okay, feedback = scheme.pair.car(result), scheme.pair.cdr(result)

			if okay != scheme.symbol.Symbol('#t'):
				total_okay = False
		
			if feedback != "":
				total_feedback.append(feedback)

		return total_okay, "\n".join(total_feedback)

	def properties(self):
		"""\
		properties() -> [(id, value, string), ...]

		Returns the properties (and values) a design has.
		"""
		i, design, rank = self.calculate()
		return design.values()

	def feedback(self):
		"""\
		feedback() -> string

		Returns the feedback for this design.
		"""
		return self.check()[1]

	def to_packet(self, sequence):
		# Preset arguments
		
		# FIXME: The calculate function gets called 3 times when we convert to a packet
		print (sequence, self.id, self.time, self.categories(), self.name, self.desc, self.used(), self.owner, self.components(), self.feedback(), self.properties())
		return netlib.objects.Design(sequence, self.id, self.time, self.categories(), self.name, self.desc, self.used(), self.owner, self.components(), self.feedback(), self.properties())

	def id_packet(cls):
		return netlib.objects.Design_IDSequence
	id_packet = classmethod(id_packet)   

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)

