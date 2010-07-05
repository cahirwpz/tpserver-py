#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from types import TupleType, ListType

def FleetClass( Object ):
	"""
	Fleet class parametrized constructor.
	"""
	class Fleet( Object ):
		@classmethod
		def InitMapper( cls, metadata, Player ):
			cls.__table__ = Table( cls.__tablename__, metadata,
					Column('object_id', ForeignKey( Object.id ), index = True, primary_key = True ),
					Column('owner_id',  ForeignKey( Player.id ), nullable = True ),
					Column('damage',    Integer, nullable = True, default = 0 ))

			mapper( cls, cls.__table__, inherits = Object, polymorphic_identity = 'Fleet', properties = {
				'owner' : relation( Player,
					uselist = False,
					backref = backref( 'fleets' ),
					cascade = 'all')
				})

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
	
	return Fleet
