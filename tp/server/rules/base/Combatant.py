class Combatant( object ):#{{{
	def dead( self ):
		"""
		Returns if the object can no-longer participate in combat.
		"""
		raise NotImplemented("Combatant.dead method not implimented.")
	
	def damage_do( self, damage ):
		"""
		damage_do([10, 3])
		damage_do(10)
		
		Does the list of discreet damage to the object. Damage should 
		either be a list of integers or an integer.
		"""
		raise NotImplemented("Combatant.damage_do method not implimented.")

	def damage_get( self, fail = False ):
		"""
		damage_get(True) -> [10, 3]
		damage_get(False) -> 3

		Returns the damage the object can do to another object.
		Damage should be returned as either a list of integers or an
		integer.
		Takes a simple argument to determine a "half fire".
		"""
		raise NotImplemented("Combatant.damage_get method not implimented.")
#}}}
