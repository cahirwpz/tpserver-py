#!/usr/bin/env python

from tp.server.model import DatabaseManager

from Common import ( FactoryMixin, RequestHandler, GetWithIDHandler,
		GetIDSequenceHandler, RemoveWithIDHandler )

class CategoryFactoryMixin( FactoryMixin ):#{{{
	def fromPacket( self, request ):
		Category = self.game.objects.use( 'Category' )

		return Category(
				owner		= self.player,
				name		= request.name,
				description	= request.description )

	def toPacket( self, request, category ):
		Category = self.protocol.use( 'Category' )

		return Category(
				request._sequence,
				category.id, 
				self.datetimeToInt( category.mtime ),
				category.name,
				category.description )
#}}}

class AddCategory( RequestHandler, CategoryFactoryMixin ):#{{{
	def __call__( self, request ):
		"""
		Request:  AddCategory :: Category
		Response: Category | Fail
		"""
		category = self.fromPacket( request )

		# TODO: What if such category already exists?

		with DatabaseManager().session() as session:
			session.add( category )

		return self.toPacket( request, category )
#}}}

class GetCategory( GetWithIDHandler, CategoryFactoryMixin ):#{{{
	"""
	Request:  GetCategory :: GetWithID
	Response: Category | Sequence + Category{2,n}
	"""
	__object__ = 'Category'

	def authorize( self, category ):
		return bool( category.owner in [ None, self.player ] )
#}}}

class GetCategoryIDs( GetIDSequenceHandler ):#{{{
	"""
	Request:  GetCategoryIDs :: GetIDSequence
	Response: IDSequence
	"""

	__packet__ = 'CategoryIDs'
	__object__ = 'Category'

	@property
	def filter( self ):
		Category = self.game.objects.use( 'Category' )

		from sqlalchemy import or_

		return or_( Category.owner == self.player, Category.owner == None )
#}}}

class RemoveCategory( RemoveWithIDHandler ):#{{{
	"""
	Request:  RemoveCategory :: GetCategory :: GetWithID
	Response: ( Okay | Fail ) | Sequence + ( Okay | Fail ){2,n}
	"""

	__object__ = 'Category'

	def authorize( self, category ):
		return bool( category.owner == self.player )
#}}}

__all__ = [ 'AddCategory', 'GetCategory', 'GetCategoryIDs', 'RemoveCategory' ]
