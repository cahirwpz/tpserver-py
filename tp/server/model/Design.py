#!/usr/bin/env python

# import pyscheme as scheme

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref, class_mapper

from Model import ModelObject, ByNameMixin

class Design( ModelObject, ByNameMixin ):
	"""
	Design of things.
	"""

	@classmethod
	def InitMapper( cls, metadata, Player ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('id',	      Integer, index = True, primary_key = True),
				Column('owner_id',    ForeignKey( Player.id ), index = True, nullable = True),
				Column('name',	      String(255), index = True, nullable = False),
				Column('description', Text, nullable = False),
				Column('comment',     Text, nullable = False, default = ''),
				Column('mtime',	      DateTime,nullable = False,
					onupdate = func.current_timestamp(), default = func.current_timestamp()),
				UniqueConstraint( 'name' ))

		mapper( cls, cls.__table__, properties = {
			'owner': relation( Player,
				uselist = False,
				backref = backref( 'designs' ))
			})
	
	def remove( self, session ):
		for component in self.components:
			component.remove( session )

		for prop in self.properties:
			prop.remove( session )

		session.commit()

		session.delete( self )


	# @property
	# def used(self):
	#	"""
	#	used -> value
	#
	#	Returns the properties (and values) a design has.
	#	"""
	#	# Need to check if the design is valid
	#	if not self.check()[0]:
	#		return -1
	#	
	#	# FIXME: This is a bit of a hack (and most probably won't work on non-MySQL)
	#	te = Object.table_extra
	#	results = select([func.sum(te.c.value).label('inplay')], 
	#							(te.c.name=='ships') & (te.c.key==repr(self.id))).execute().fetchall()
	#	try:
	#		inplay = long(results[0]['inplay'])
	#	except (KeyError, ValueError, TypeError):
	#		inplay = 0
	#
	#	# FIXME: This is hardcoded currently
	#	t  = Order.table
	#	te = Order.table_extra
	#	j  = join(Order.table, Order.table_extra)
	#	results = select([func.sum(te.c.value).label('beingbuilt')], 
	#						(te.c.name=='ships') & (te.c.key==repr(self.id)) & (t.c.type=='sorders.Build'),
	#						from_obj=[j]
	#					).execute().fetchall()
	#
	#	try:
	#		beingbuilt = long(results[0]['beingbuilt'])
	#	except (KeyError, ValueError, TypeError):
	#		beingbuilt = 0
	#	
	#	return inplay+beingbuilt

	# @property
	# def properties(self):
	#	"""
	#	properties -> [(id, value, string), ...]
	#
	#	Returns the properties (and values) a design has.
	#	"""
	#	i, design = self.calculate()
	#	return [(x[0], x[2]) for x in design.values()]

	# @property
	# def feedback(self):
	#	"""
	#	feedback -> string
	#
	#	Returns the feedback for this design.
	#	"""
	#	return self.check()[1]

	# @property
	# def rank(self):
	#	if len(self.components) <= 0:
	#		return {}
	#
	#	# FIXME: This is a hack, there should be a better way to do this
	#	tc = Component.table_property
	#	tpr = Property.table
	#	j = join(tc, tpr)
	#
	#	results = select([tc.c.property.label('id'), tpr.c.rank.label('rank')], tc.c.component.in_(*zip(*self.components)[0]), \
	#							from_obj=[j], order_by=[tpr.c.rank], distinct=True).execute().fetchall()
	#
	#	ranks = {}
	#	for result in results:
	#		rank, id = result['rank'], result['id']
	#	
	#		if not ranks.has_key(rank):
	#			ranks[rank] = []
	#		ranks[rank].append(id)
	#
	#	return ranks

	# def calculate(self):
	#	"""
	#	calculate() -> Interpretor, Design
	#
	#	Calculates all the properties on a design. 
	#	Returns the Interpretor (used to create the design and the actual design).
	#	"""
	#	if hasattr(self, '_calculate'):
	#		return self._calculate
	#	i = scheme.make_interpreter()
	#
	#	# Step 1 -------------------------------------
	#
	#	ranks = self.rank()
	#	debug( "The order I need to calculate stuff in is, %s" % ranks )
	#
	#	# Step 2 -------------------------------------
	#
	#	# The design object
	#	class Design(dict):
	#		pass
	#
	#	design = Design()
	#	scheme.environment.defineVariable(scheme.symbol.Symbol('design'), design, i.get_environment())
	#
	#	# Step 3 -------------------------------------
	#	for rank in ranks.keys():
	#		for property_id in ranks[rank]:
	#			property = Property(property_id)
	#
	#			# Where we will store the values as calculated
	#			bits = []
	#	
	#			# Get all the components we contain
	#			for component_id, amount in self.components:
	#				# Create the component object
	#				component = Component(component_id)
	#
	#				# Calculate the actual value for this design
	#				value = component.property(property_id)
	#				if value:
	#					debug( "Now evaluating %s" % value )
	#					value = i.eval(scheme.parse("""( %s design)""" % value))
	#
	#					debug( "The value calculated for component %i was %r" % (component_id, value) )
	#				
	#					for x in range(0, amount):
	#						bits.append(value)
	#
	#			debug( "All the values calculated where %s", bits )
	#			bits_scheme = "(list"
	#			for bit in bits:
	#				bits_scheme += " " + str(bit).replace('L', '')
	#			bits_scheme += ")"
	#			debug( "In scheme that is %s", bits_scheme )
	#		
	#			debug( "(let ((bits %s)) (%s design bits))" % (bits_scheme, property.calculate) )
	#			total = i.eval(scheme.parse("""(let ((bits %s)) (%s design bits))""" % (bits_scheme, property.calculate)))
	#			value, display = scheme.pair.car(total), scheme.pair.cdr(total)
	#
	#			debug( "In total I got '%i' which will be displayed as '%s'" % (value, display) )
	#			design[property.name] = (property_id, value, display)
	#
	#			def t(design, name=property.name):
	#				return design[name][1]
	#			
	#			i.install_function('designtype.'+property.name, t)
	#			
	#	debug( "The final properties we have are %s" % design.items() )
	#	self._calculate = (i, design)
	#	return i, design

	# def check(self):
	#	"""
	#	check() -> Interpretor, Design
	#
	#	Checks the requirements of a design.
	#	"""
	#	if hasattr(self, '_check'):
	#		return self._check
	#	
	#	# Step 1, calculate the properties
	#	i, design = self.calculate()
	#	
	#	total_okay = True
	#	total_feedback = []
	#
	#	# Step 2, calculate the requirements for the properties
	#	ranks = self.rank()
	#	for rank in ranks.keys():
	#		for property_id in ranks[rank]:
	#
	#			property = Property(property_id)
	#			if property.requirements == '':
	#				debug( "Property with id (%i) doesn't have any requirements" % property_id )
	#				continue
	#		
	#			debug( "Now checking the following requirement" )
	#			debug( str( property.requirements ) )
	#			result = i.eval(scheme.parse("""(%s design)""" % property.requirements))
	#			debug( "Result was: %s", result )
	#			okay, feedback = scheme.pair.car(result), scheme.pair.cdr(result)
	#
	#			if okay != scheme.symbol.Symbol('#t'):
	#				total_okay = False
	#	
	#			if feedback != "":
	#				total_feedback.append(feedback)
	#			
	#	# Step 3, calculate the requirements for the components
	#	for component_id, amount in self.components:
	#		component = Component(component_id)
	#		if component.requirements == '':
	#			debug( "Component with id (%i) doesn't have any requirements" % component_id )
	#			continue
	#		
	#		debug( "Now checking the following requirement" )
	#		debug( str( component.requirements ) )
	#		result = i.eval(scheme.parse("""(%s design)""" % component.requirements))
	#		debug( "Result was: %s" % result )
	#		okay, feedback = scheme.pair.car(result), scheme.pair.cdr(result)
	#
	#		if okay != scheme.symbol.Symbol('#t'):
	#			total_okay = False
	#	
	#		if feedback != "":
	#			total_feedback.append(feedback)
	#	
	#	self._check = (total_okay, "\n".join(total_feedback))
	#	return total_okay, "\n".join(total_feedback)

	def __str__(self):
		return '<%s@%s id="%s" name="%s">' % ( self.__origname__, self.__game__.name, self.id, self.name )

class DesignCategory( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata, Design, Category ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('design_id',   ForeignKey( Design.id ), index = True, primary_key = True),
				Column('category_id', ForeignKey( Category.id ), index = True, primary_key = True))

		cols = cls.__table__.c

		Index('ix_%s_design_category' % cls.__tablename__, cols.design_id, cols.category_id)

		mapper( cls, cls.__table__, properties = {
			'design': relation( Design,
				uselist = False),
			'category': relation( Category,
				uselist = False)
			})

		class_mapper( Design ).add_property( 'categories',
			relation( Category,
				secondary = cls.__table__,
				backref = backref( 'designs' )))

	def __str__( self ):
		return '<%s@%s id="%s" design="%s", category="%s">' % \
				( self.__origname__, self.__game__.name, self.design.name, self.category.name )

class DesignComponent( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata, Design, Component ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('design_id',    ForeignKey( Design.id ), primary_key = True ),
				Column('component_id', ForeignKey( Component.id ), primary_key = True ),
				Column('amount',       Integer, nullable = False, default = 1 ))

		cols = cls.__table__.c

		Index('ix_%s_design_component' % cls.__tablename__, cols.design_id, cols.component_id)

		mapper( cls, cls.__table__, properties = {
			'design': relation( Design,
				uselist = False,
				backref = backref( 'components' )),
			'component': relation( Component,
				uselist = False,
				backref = backref( 'designs' ))
			})

	def __str__( self ):
		return '<%s@%s id="%s" design="%s", component="%s">' % \
				( self.__origname__, self.__game__.name, self.design.name, self.component.name )

class DesignProperty( ModelObject ):
	@classmethod
	def InitMapper( cls, metadata, Design, Property ):
		cls.__table__ = Table( cls.__tablename__, metadata,
				Column('design_id',   ForeignKey( Design.id ), primary_key = True ),
				Column('property_id', ForeignKey( Property.id ), primary_key = True ),
				Column('value',       Text, nullable = False, default = """(lambda (design) 1)""" ))

		cols = cls.__table__.c

		Index('ix_%s_design_property' % cls.__tablename__, cols.design_id, cols.property_id)

		mapper( cls, cls.__table__, properties = {
			'design': relation( Design,
				uselist = False,
				backref = backref( 'properties' )),
			'property': relation( Property,
				uselist = False,
				backref = backref( 'designs' ))
			})

	def __str__( self ):
		return '<%s@%s id="%s" design="%s", property="%s">' % \
				( self.__origname__, self.__game__.name, self.design.name, self.property.name )

__all__ = [ 'Design', 'DesignCategory', 'DesignComponent', 'DesignProperty' ]
