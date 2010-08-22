#!/usr/bin/env python

from logging import *
from tp.server.model import Model

from Common import ( MustBeLogged, FactoryMixin, RequestHandler,
		GetWithIDSlotHandler, RemoveWithIDSlotHandler )

class MessageFactoryMixin( FactoryMixin ):
	def fromPacket( self, request ):
		Message = self.model.use( 'Message' )

		return Message(
					subject	= request.subject,
					body	= request.body,
					turn	= self.game.turn )

	def toPacket( self, request, obj ):
		# FIXME: The reference system needs to be added and so does the turn
		Message = self.protocol.use( 'Message' )

		return Message( request._sequence,
				obj.board_id,
				obj.slot,
				[],	# not used as of TP03
				obj.subject,
				str( obj.body ),
				obj.turn,
				[] # TODO: references
				)

class PostMessage( RequestHandler, MessageFactoryMixin ):
	"""
	Request:  PostMessage :: Message
	Response: Okay | Fail
	"""
	def authorize( self, obj ):
		return True

	@MustBeLogged
	def __call__( self, request ):
		Container = self.model.use( 'Board' )

		container = Container.ById( request.id )

		if container:
			if self.authorize( container ):
				slot = request.slot if request.slot < len( container.messages ) else -1

				message = self.fromPacket( request ) 

				if slot == -1:
					container.messages.append( message )
				else:
					container.messages.insert( slot, message )

				Model.add( container )

				if slot == -1:
					slot = len( container.messages )

				response = self.Okay( request, "Message posted on %s with id = %d in slot %d." % ( Container.__origname__, request.id, slot ) )
			else:
				debug( "No permission for %s with id %s.", Container.__origname__, request.id ) 
				response = self.Fail( request, "PermissionDenied", "You cannot access %s with id = %d." % ( Container.__origname__, request.id ) )
		else:
			debug( "No such %s with id %s.", Container.__origname__, request.id ) 
			response = self.Fail( request, "NoSuchThing", "No %s with id = %d." % ( Container.__origname__, request.id ) )

		return response 

class GetMessage( GetWithIDSlotHandler, MessageFactoryMixin ):
	"""
	Request:  GetMessage :: GetWithIDSlot
	Response: Message | Sequence + (Message | Fail){2,n}
	"""
	__container__ = 'Board'

	def getItem( self, board, slot ):
		try:
			return board.messages[ slot - 1 ]
		except IndexError:
			return None

class RemoveMessage( RemoveWithIDSlotHandler ):
	"""
	Request:  RemoveMessage :: GetMessage :: GetWithIDSlot
	Response: ( Okay | Fail ) | Sequence + ( Okay | Fail ){2,n}
	"""
	__container__ = 'Board'

__all__ = [ 'PostMessage', 'GetMessage', 'RemoveMessage' ]
