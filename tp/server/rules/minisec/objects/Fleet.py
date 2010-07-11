#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper

from types import TupleType, ListType

class Fleet( object ):#{{{
	__attributes__ = [ 'owner', 'damage', 'ships' ]

	@classmethod
	def InitMapper( cls, metadata, Object ):
		mapper( cls, inherits = Object, polymorphic_identity = 'Fleet' )

	@property
	def damage( self ):
		try:
			return self['damage'].value
		except KeyError:
			return 0

	@damage.setter
	def damage( self, value ):
		try:
			self['damage'].value = value
		except KeyError:
			NumberParam = self.__game__.objects.use('NumberParam')

			self['damage'] = NumberParam( value = value )

	@property
	def owner( self ):
		try:
			return self['owner'].player
		except KeyError:
			return None

	@owner.setter
	def owner( self, value ):
		if value is not None:
			try:
				self['owner'].player = value
			except KeyError:
				PlayerParam = self.__game__.objects.use('PlayerParam')

				self['owner'] = PlayerParam( player = value )

	@property
	def ships( self ):
		try:
			return self['ships'].designs
		except KeyError:
			DesignListParam = self.__game__.objects.use('DesignListParam')

			self['ships'] = DesignListParam()

			return self['ships'].designs

	@ships.setter
	def ships( self, value ):
		if value is not None:
			DesignListParam = self.__game__.objects.use('DesignListParam')

			try:
				self['ships'].designs = value
			except (KeyError, AttributeError):
				self['ships'] = DesignListParam()
				self['ships'].designs = value

	@property
	def typeno( self ):
		return 4

	orderclasses = ('tp.server.rules.base.orders.NOp', 
					'tp.server.rules.minisec.orders.Move',
					'tp.server.rules.minisec.orders.SplitFleet',
					'tp.server.rules.base.orders.MergeFleet',
					'tp.server.rules.base.orders.Colonise',)
	
	def fn_ships(self, value=None):
		if value == None:
			return self.ships.items()

	def fn_damage(self, value=None):
		if value == None:
			return sum(map(sum, self.damage.values()))

			totaldamage = 0
			for type, damage in self.damage:
				if type in self.ships.keys():
					for d in damage:
						totaldamage += damage
			
			return totaldamage
			
	def tidy(self):
		"""
		Fix up the ships and damage stuff.
		"""
		# Run a consistancy check
		# Check the ships actually exist
		for t, number in self.ships.items():
			if number < 1:
				del self.ships[t]

		# Check the damage goes to the right place
		for t, damage in self.damage.items():
			if not t in self.ships.keys():
				del self.damage[t]

	def ghost(self):
		"""
		Returns if the fleet has no ships.
		"""
		self.tidy()
		return len(self.ships.keys()) < 1

	#############################################
	# Movement functions
	#############################################
	def speed(self):
		"""
		Returns the maximum speed of the fleet.
		"""
		return self.ship_speed[max(self.ships.keys())]
	
	#############################################
	# Combat functions
	#############################################

	def dead(self):
		"""
		Checks if this object is a can still participate in combat.
		"""
		return self.ghost() or self.ships.keys() == [0,]
		
	def damage_do(self, amount):
		"""
		Damages a fleet. Can be called with either a single
		integer or a tuple of integers.
		"""
		if type(amount) in (TupleType, ListType):
			for a in amount:
				self.damage_do(a)
			return

		self.tidy()

		# Find the largest ship type.
		s = self.ships.keys()
		s.sort()
		s.reverse()
		t = s[0]
	
		if not self.damage.has_key(t):
			self.damage[t] = []
		damage = self.damage[t]

		# Condense the damage
		if len(damage)+1 > self.ships[t]:
			damage.sort()
			if damage[0] + amount >= self.ship_hp[t]:
				damage[-1] += amount
			else:
				damage[0] += amount
		else:
			damage.append(amount)
		
		if damage[-1] >= self.ship_hp[t]:
			self.ships[t] -= 1
			if self.ships[t] < 1:
				del self.ships[t]
			del damage[-1]

	def damage_get(self, fail=False):
		"""
		Returns the amount of damage this fleet can do.
		"""
		r = []
		for type, no in self.ships.items():
			r.extend([self.ship_damage[type][fail]] * no)
		return r
#}}}

__all__ = [ 'Fleet' ]
