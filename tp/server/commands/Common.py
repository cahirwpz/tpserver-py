#!/usr/bin/env python

import time

from tp.server.bases import NoSuchThing, PermissionDenied

from tp.server.db import DatabaseManager
from tp.server.logging import msg

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
		Fail = self.protocol.objects.use( 'Fail' )

		return Fail( request._sequence, 'Protocol', 'Command not handled!' )
#}}}

class GetWithIDHandler( RequestHandler ):#{{{
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

	def __call__( self, request ):
		Object = self.game.objects.use( self.__object__ )

		Packet, Sequence, Fail = self.protocol.use( self.__packet__, 'Sequence', 'Fail' )

		response = []

		for id in request.ids:
			obj = self.fetch( Object, id )

			if obj:
				if self.authorize( obj ):
					response.append( self.toPacket( request, obj ) )
				else:
					msg( "${yel1}No permission for %s with id %s.${coff}" % ( Object.__origname__, id ) )
					response.append( Fail( request._sequence, "PermissionDenied", "You cannot read %s with id = %d." % ( Object.__origname__, id ), []) )
			else:
				msg( "${yel1}No such %s with id %s.${coff}" % ( Object.__origname__, id ) )
				response.append( Fail( request._sequence, "NoSuchThing", "No %s with id = %d." % ( Object.__origname__, id ), []) )

		if len( response ) > 1:
			response.insert( 0, Sequence( request._sequence, len( response ) ) )

		return response
#}}}

class RemoveWithIDHandler( RequestHandler ):#{{{
	__object__ = None

	def authorize( self, obj ):
		"""
		Returns true when the user is allowed to removed an object, false in other case.
		"""
		return False

	def __call__( self, request ):
		Object = self.game.objects.use( self.__object__ )

		Okay, Fail, Sequence = self.protocol.objects.use( 'Okay', 'Fail', 'Sequence' )

		response = []

		for id in request.ids:
			obj = Object.ById( id )

			if obj:
				if self.authorize( obj ):
					with DatabaseManager().session() as session:
						session.remove( obj )

					response.append( Okay( request._sequence, "%s with id = %d removed." % ( Object.__origname__, id ) ) )
				else:
					msg( "${yel1}No permission for %s with id %s.${coff}" % ( Object.__origname__, id ) )
					response.append( Fail( request._sequence, "PermissionDenied", "You cannot remove %s with id = %d." % ( Object.__origname__, id ), []) )
			else:
				msg( "${yel1}No such %s with id %s.${coff}" % ( Object.__origname__, id ) )
				response.append( Fail( request._sequence, "NoSuchThing", "No %s with id = %d." % ( Object.__origname__, id ), []) )

		if len( response ) > 1:
			response.insert( 0, Sequence( request._sequence, len( response ) ) )

		return response
#}}}

class IDSequence( object ):#{{{
	def __init__( self, key, remaining, objects ):
		self.key       = key
		self.remaining = remaining
		self.objects   = objects
	#}}}

class IDSequenceFactoryMixin( FactoryMixin ):#{{{
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
	__packet__ = None

	@property
	def filter( self ):
		pass

	def __call__( self, request ):
		Object = self.game.objects.use( self.__object__ )

		Fail = self.protocol.use( 'Fail' )

		last = Object.query().filter( self.filter ).order_by( Object.mtime ).first()

		key = long( last.mtime.strftime('%s') ) if last else -1

		if request.key != -1 and key != request.key:
			return Fail( request._sequence, "NoSuchThing", "Key %s is no longer valid, please get a new key." % request.key )

		total = Object.query().filter( self.filter ).count()
		
		if request.start + request.amount > total:
			msg( "Requested %d items starting at %d. Actually %s." % ( request.amount, request.amount, total ) )
			return Fail( request._sequence, "NoSuchThing", "Requested too many IDs. (Requested %s, actually %s)" % (request.start + request.amount, total))

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
	__packet__    = None

	def getItems( self, obj ):
		raise NotImplementedError

	def authorize( self, obj ):
		"""
		Returns true if the user is allowed to fetch an object from container, false in other case.
		"""
		return True

	def __call__( self, request ):
		"""
		request - Get request to be processes, it must have the following
			request.id		- The id of the container
			request.slots	- The slots to be gotten
		"""
		Container = self.game.objects.use( self.__container__ )

		Packet, Sequence, Fail = self.protocol.use( self.__packet__, 'Sequence', 'Fail' )

		response = []

		container = Container.ById( request.id )

		if container:
			if self.authorize( container ):
				for slot in request.slots:
					obj = self.getItem( container, slot )

					if obj:
						response.append( self.toPacket( request, obj ) )
					else:
						msg( "${yel1}No such %s with id %s.${coff}" % ( Container.__origname__, request.id ) )
						response.append( Fail( request._sequence, "NoSuchThing", "No %s with id = %d." % (Container.__origname__, request.id), []) )
			else:
				msg( "${yel1}No permission for %s with id %s.${coff}" % ( Container.__origname__, request.id ) )
				response.append( Fail( request._sequence, "PermissionDenied", "You cannot read %s with id = %d." % ( Container.__origname__, request.id ), []) )
		else:
			msg( "${yel1}No such %s with id %s.${coff}" % ( Container.__origname__, request.id ) )
			response.append( Fail( request._sequence, "NoSuchThing", "No %s with id = %d." % ( Container.__origname__, request.id ), []) )

		return response
#}}}

__all__ = [ 'FactoryMixin', 'RequestHandler', 'GetWithIDHandler',
			'RemoveWithIDHandler', 'GetIDSequenceHandler', 'GetWithIDSlotHandler' ]
