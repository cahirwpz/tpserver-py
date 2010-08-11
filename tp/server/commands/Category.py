#!/usr/bin/env python

from Common import ( MustBeLogged, FactoryMixin, RequestHandler, GetWithIDHandler,
		GetIDSequenceHandler, RemoveWithIDHandler )

from tp.server.model import Model, and_, or_

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
	@MustBeLogged
	def __call__( self, request ):
		"""
		Request:  AddCategory :: Category
		Response: Category | Fail
		"""
		category = self.fromPacket( request )

		Category = self.game.objects.use( 'Category' )

		if Category.query().filter( and_( Category.name == category.name,
					or_( Category.owner_id == self.player.id, Category.owner_id == None ))).count():
			return self.Fail( request, "PermissionDenied",
					"Category named %s already exists!" % category.name )

		Model.add( category )

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
