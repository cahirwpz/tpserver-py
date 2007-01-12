"""\
Design of things.
"""
# Module imports
from sqlalchemy import *

# Local imports
from tp import netlib
from SQL import SQLBase

from Object import Object
from Order import Order
from Component import Component
from Property import Property

import pyscheme as scheme

class Design(SQLBase):
	table = Table('design',
		Column('id',	    Integer,     nullable=False, index=True, primary_key=True),
		Column('name',	    String(255), nullable=False, index=True),
		Column('desc',      Binary,      nullable=False),
		Column('owner',     Integer,     nullable=False),
		Column('time',	    DateTime,    nullable=False, index=True, onupdate=func.current_timestamp()),
		ForeignKeyConstraint(['owner'], ['user.id']),
	)
	table_category = Table('design_category',
		Column('design',    Integer,  nullable=False, index=True, primary_key=True),
		Column('category',  Integer,  nullable=False, index=True, primary_key=True),
		Column('comment',   Binary,   nullable=False, default=''),
		Column('time',	    DateTime, nullable=False, index=True, onupdate=func.current_timestamp()),
		ForeignKeyConstraint(['design'],   ['design.id']),
		ForeignKeyConstraint(['category'], ['category.id']),
	)
	table_component = Table('design_component',
		Column('design',    Integer,  nullable=False, index=True, primary_key=True),
		Column('component', Integer,  nullable=False, index=True, primary_key=True),
		Column('amount',    Integer,  nullable=False, default=0),
		Column('comment',   Binary,   nullable=False, default=''),
		Column('time',	    DateTime, nullable=False, index=True, onupdate=func.current_timestamp()),
		ForeignKeyConstraint(['design'],   ['design.id']),
		ForeignKeyConstraint(['component'], ['component.id']),
	)
	
	def load(self, id):
		"""\
		load(id)

		Loads a thing from the database.
		"""
		SQLBase.load(self, id)

		# Load the categories now
		self.categories = self.get_categories()

		# Load the properties now
		self.components = self.get_components()

	def save(self):
		"""\
		save()

		Saves a thing to the database.
		"""
		SQLBase.save(self)

		# Save the categories now
		t = self.table_category
		current = self.get_categories()
		for cid in current+self.categories:
			if cid in current and not cid in self.categories:
				# Remove the category
				results = t.delete((t.c.design==self.id) & (t.c.category==cid)).execute()
			
			if cid not in self.categories and cid in current:
				# Add the category
				results = t.insert().execute(design=self.id, category=cid)

		# Save the components now
		t = self.table_components
		current = self.get_components()
		
		ct = {}
		for cid, amount in current:
			ct[cid] = [amount, None]
		for cid, amount in self.components:
			if ct.has_key(cid):
				ct[cid][1] = amount
			else:
				ct[cid] = [None, amount]

		for cid, values in ct.items():
			start, end = values
		
			if end == None or end < 1:
				results = t.delete(t.c.design==self.id & t.c.component==cid).execute()
	
			if start != end:
				results = t.update().execute(design=self.id, category=cid, amount=amount)
			
	def set_ignore(self, value):
		return
	
	def get_categories(self):
		"""\
		get_categories -> [id, ...]

		Returns the categories the design is in.
		"""
		t = self.table_category

		if not hasattr(self, '_categories'):
			if not hasattr(self, 'id'):
				self._categories = []
			else:
				results = select([t.c.category], t.c.design==self.id).execute().fetchall()
				self._categories = [x['category'] for x in results]
		return self._categories
		
	def get_components(self):
		"""\
		get_components -> [id, ...]

		Returns the components the design contains.
		"""
		t = self.table_component

		if not hasattr(self, '_components'):
			if not hasattr(self, 'id'):
				self._components = []
			else:
				results = select([t.c.component, t.c.amount], t.c.design==self.id).execute().fetchall()
				self._components = [(x['component'], x['amount']) for x in results]
		return self._components
	
	def used(self):
		"""\
		used -> value

		Returns the properties (and values) a design has.
		"""
		# Need to check if the design is valid
		if not self.check()[0]:
			return -1
		
		# FIXME: This is a bit of a hack (and most probably won't work on non-MySQL)
		te = Object.table_extra
		results = select([func.sum(te.c.value).label('inplay')], 
								(te.c.name=='ships') & (te.c.key==repr(self.id))).execute().fetchall()
		try:
			inplay = long(results[0]['inplay'])
		except (KeyError, ValueError, TypeError):
			inplay = 0
	
		# FIXME: This is hardcoded currently
		t  = Order.table
		te = Order.table_extra
		j  = join(Order.table, Order.table_extra)
		results = select([func.sum(te.c.value).label('beingbuilt')], 
							(te.c.name=='ships') & (te.c.key==repr(self.id)) & (t.c.type=='sorders.Build'),
							from_obj=[j]
						).execute().fetchall()

		try:
			beingbuilt = long(results[0]['beingbuilt'])
		except (KeyError, ValueError, TypeError):
			beingbuilt = 0
		
		return inplay+beingbuilt
	used = property(used)

	def properties(self):
		"""\
		properties -> [(id, value, string), ...]

		Returns the properties (and values) a design has.
		"""
		i, design = self.calculate()
		return [(x[0], x[2]) for x in design.values()]
	properties = property(properties)

	def feedback(self):
		"""\
		feedback -> string

		Returns the feedback for this design.
		"""
		return self.check()[1]
	feedback = property(feedback)

	def rank(self):
		if len(self.components) <= 0:
			return {}

		# FIXME: This is a hack, there should be a better way to do this
		tc = Component.table_property
		tpr = Property.table
		j = join(tc, tpr)

		results = select([tc.c.property.label('id'), tpr.c.rank.label('rank')], tc.c.component.in_(*zip(*self.components)[0]), \
								from_obj=[j], order_by=[tpr.c.rank], distinct=True).execute().fetchall()

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
		if hasattr(self, '_calculate'):
			return self._calculate
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
				for component_id, amount in self.components:
					# Create the component object
					component = Component(component_id)

					# Calculate the actual value for this design
					value = component.property(property_id)
					if value:
						print "Now evaluating", value
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
				design[property.name] = (property_id, value, display)

				def t(design, name=property.name):
					return design[name][1]
				
				i.install_function('designtype.'+property.name, t)
				
		print "The final properties we have are", design.items()
		self._calculate = (i, design)
		return i, design
	
	def check(self):
		"""\
		check() -> Interpretor, Design

		Checks the requirements of a design.
		"""
		if hasattr(self, '_check'):
			return self._check
		
		# Step 1, calculate the properties
		i, design = self.calculate()
		
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
		for component_id, amount in self.components:
			component = Component(component_id)
			if component.requirements == '':
				print "Component with id (%i) doesn't have any requirements" % component_id
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
		
		self._check = (total_okay, "\n".join(total_feedback))
		return total_okay, "\n".join(total_feedback)

	def to_packet(self, sequence):
		# FIXME: The calculate function gets called 3 times when we convert to a packet
		print (sequence, self.id, self.time, self.categories, self.name, self.desc, self.used, self.owner, self.components, self.feedback, self.properties)
		return netlib.objects.Design(sequence, self.id, self.time, self.categories, self.name, self.desc, self.used, self.owner, self.components, self.feedback, self.properties)

	def from_packet(self, packet):
		# Check the design meets a few guide lines
		
		# FIXME: Check each component exists and the amount is posative
		for id, amount in packet.components:
			pass
		
		# Check we have at least one category
		if len(packet.categories) < 1:
			raise ValueError("Designs must have atleast one category")
		else:
			# FIXME: Check that the categories are valid
			pass
		
		# FIXME: Check the owner is sane
	
		# FIXME: Check the id
		if packet.id != -1:
			self.id = packet.id
			
		for key in ["categories", "name", "desc", "owner", "components"]:
			setattr(self, key, getattr(packet, key))

	def id_packet(cls):
		return netlib.objects.Design_IDSequence
	id_packet = classmethod(id_packet)   

	def __str__(self):
		return "<Component id=%s name=%s>" % (self.id, self.name)

