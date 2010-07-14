#!/usr/bin/env python

class Action( object ):#{{{
	def __call__( self, *args, **kwargs ):
		pass
#}}}

class UniverseAction( object ):#{{{
	"""
	Anything that happens without requiring the user to initiate.
	Some examples would be Combat or growing the Population.
	"""

	def __walk( self, top, order, callback, *args, **kwargs ):
		"""
		Walks around the universe and calls a command for each object.
		
		If the first argument is "before" parents will be called before there children.
		If the first argument is "after" parents will be called after there children.
		"""
		if order == "before":
			callback(top, *args, **kwargs)

		for id in top.contains():
			self.__walk(Object(id), order, callback, *args, **kwargs)

		if order == "after":
			callback(top, *args, **kwargs)

	def __call__( self, top, order, callback, *args, **kwargs ):
		"""
		Given the universe as an interable object. It impliments most
		functions of dictionaries.
		A parent will appear before it's child.
		"""
		self.__walk( top, order, callback, *args, **kwargs )
#}}}

__all__ = [ 'Action', 'UniverseAction' ]
