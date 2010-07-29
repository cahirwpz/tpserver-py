#!/usr/bin/env python

import time

from tp.server.model import DatabaseManager
from tp.server.logging import msg

def MustBeLogged( func ):#{{{
	def check( self, request ):
		"""
		Checks if the user is logged in (TODO: and the turn is not being currently processed)
		"""
		if self.player is None:
			Fail = self.protocol.use( 'Fail' )

			return Fail( request._sequence, "UnavailableTemporarily", "You need to be logged in to use this functionality.", [] )

		return func( self, request )
	
	return check
#}}}

class FactoryMixin( object ):#{{{
	def datetimeToInt( self, t ):
		return int( time.mktime( time.strptime( t.ctime() ) ) )
#}}}

class RequestHandler( object ):#{{{
	def __init__( self, protocol, context ):
		self.protocol = protocol
		self.context  = context

	@property
	def player( self ):
		return self.context.player

	@property
	def game( self ):
		return self.context.game

	def __call__( self, request ):
		return self.Fail( request, 'Protocol', 'Command not handled!' )

	def Okay( self, request, result ):
		return self.protocol['Okay']( request._sequence, result )

	def Fail( self, request, code, result ):
		return self.protocol['Fail']( request._sequence, code, result, [] )

	def Sequence( self, request, length ):
		return self.protocol['Sequence']( request._sequence, length )
#}}}

class WithIDHandler( RequestHandler ):#{{{
	__object__ = None
	__packet__ = None

	def authorize( self, obj ):
		"""
		Returns true if the user is allowed to fetch an object, false in other case.
		"""
		return True

	def fetch( self, obj, id ):
		"""
		Fetches object with given id number.
		"""
		return obj.ById( id )

	def process( self, request, obj ):
		raise NotImplementedError

	@MustBeLogged
	def __call__( self, request ):
		Object = self.game.objects.use( self.__object__ )

		response = []

		for id in request.ids:
			obj = self.fetch( Object, id )

			if obj:
				if self.authorize( obj ):
					response.append( self.process( request, obj ) )
				else:
					msg( "${yel1}No permission for %s with id %s.${coff}" % ( Object.__origname__, id ) )
					response.append( self.Fail( request, "PermissionDenied", "You cannot read %s with id = %d." % ( Object.__origname__, id ) ) )
			else:
				msg( "${yel1}No such %s with id %s.${coff}" % ( Object.__origname__, id ) )
				response.append( self.Fail( request, "NoSuchThing", "No %s with id = %d." % ( Object.__origname__, id ) ) )

		if len( response ) > 1:
			response.insert( 0, self.Sequence( request, len( response ) ) )

		return response
#}}}

class GetWithIDHandler( WithIDHandler ):#{{{
	__object__ = None

	def process( self, request, obj ):
		return self.toPacket( request, obj )
#}}}

class RemoveWithIDHandler( WithIDHandler ):#{{{
	__object__ = None

	def process( self, request, obj ):
		Object = self.game.objects.use( self.__object__ )

		with DatabaseManager().session() as session:
			session.remove( obj )

		return self.Okay( request, "%s with id = %d removed." % ( Object.__origname__, id ) )
#}}}

class IDSequence( object ):#{{{
	def __init__( self, key, remaining, objects ):
		self.key       = key
		self.remaining = remaining
		self.objects   = objects
	#}}}

class IDSequenceFactoryMixin( FactoryMixin ):#{{{
	__packet__ = None

	def toPacket( self, request, obj ):
		Packet = self.protocol.use( self.__packet__ )

		return Packet(
				request._sequence,
				obj.key,
				obj.remaining,
				[ ( obj.id, self.datetimeToInt( obj.mtime ) ) for obj in obj.objects ] )
#}}}

class GetIDSequenceHandler( RequestHandler, IDSequenceFactoryMixin ):#{{{
	__object__ = None

	@property
	def filter( self ):
		pass

	@MustBeLogged
	def __call__( self, request ):
		Object = self.game.objects.use( self.__object__ )

		last = Object.query().filter( self.filter ).order_by( Object.mtime ).first()

		key = long( last.mtime.strftime('%s') ) if last else -1

		if request.key != -1 and key != request.key:
			return self.Fail( request, "NoSuchThing", "Key %s is no longer valid, please get a new key." % request.key )

		total = Object.query().filter( self.filter ).count()
		
		if request.start + request.amount > total:
			msg( "Requested %d items starting at %d. Actually %s." % ( request.amount, request.amount, total ) )
			return self.Fail( request, "NoSuchThing", "Requested too many IDs. (Requested %s, actually %s)" % (request.start + request.amount, total))

		if request.amount == -1:
			# if amount equals to -1 then only give number of available items
			response = IDSequence( key, total, [] )
		else:
			response = IDSequence( key, 
					total - ( request.start + request.amount ),
					Object.query().filter( self.filter ).order_by( Object.mtime )[ request.start : request.start + request.amount ] )

		return self.toPacket( request, response )
	#}}}

class GetWithIDSlotHandler( RequestHandler ):#{{{
	__container__ = None

	def getItem( self, container, number ):
		raise NotImplementedError

	def authorize( self, obj ):
		"""
		Returns true if the user is allowed to fetch an object from container, false in other case.
		"""
		return True

	def fetch( self, obj, id ):
		"""
		Fetches object with given id number.
		"""
		return obj.ById( id )

	@MustBeLogged
	def __call__( self, request ):
		"""
		request - Get request to be processes, it must have the following
			request.id		- The id of the container
			request.slots	- The slots to be gotten
		"""
		Container = self.game.objects.use( self.__container__ )

		response = []

		container = self.fetch( Container, request.id )

		if container:
			if self.authorize( container ):
				for slot in request.slots:
					obj = self.getItem( container, slot )

					if obj:
						response.append( self.toPacket( request, obj ) )
					else:
						msg( "${yel1}No such %s with id %s.${coff}" % ( Container.__origname__, request.id ) )
						response.append( self.Fail( request, "NoSuchThing", "No %s with id = %d." % ( Container.__origname__, request.id ) ) )
			else:
				msg( "${yel1}No permission for %s with id %s.${coff}" % ( Container.__origname__, request.id ) )
				response.append( self.Fail( request, "PermissionDenied", "You cannot read %s with id = %d." % ( Container.__origname__, request.id ) ) )
		else:
			msg( "${yel1}No such %s with id %s.${coff}" % ( Container.__origname__, request.id ) )
			response.append( self.Fail( request, "NoSuchThing", "No %s with id = %d." % ( Container.__origname__, request.id ) ) )

		return response
#}}}

__all__ = [ 'FactoryMixin', 'RequestHandler', 'GetWithIDHandler',
			'RemoveWithIDHandler', 'GetIDSequenceHandler', 'GetWithIDSlotHandler' ]
