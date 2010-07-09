class ActionMixin( object ):#{{{
	"""
	Anything that happens without requiring the user to initiate.
	Some examples would be Combat or growing the Population.
	"""

	def do( universe ):
		"""
		Given the universe as an interable object. It impliments most
		functions of dictionaries.
		A parent will appear before it's child.
		"""
#}}}
