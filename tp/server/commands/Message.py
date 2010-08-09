#!/usr/bin/env python

from tp.server.logging import msg
from tp.server.model import DatabaseManager

from Common import ( MustBeLogged, FactoryMixin, RequestHandler,
		GetWithIDSlotHandler, RemoveWithIDSlotHandler )

class MessageFactoryMixin( FactoryMixin ):#{{{
	def fromPacket( self, request ):
		Message = self.game.objects.use( 'Message' )

		return Message(
					subject	= request.subject,
					body	= request.body,
					turn	= self.game.turn )

	def toPacket( self, request, obj ):
		# FIXME: The reference system needs to be added and so does the turn
		Message = self.protocol.use( 'Message' )

		return Message( request._sequence,
				obj.board_id,
				obj.number,
				[],	# not used as of TP03
				obj.subject,
				str( obj.body ),
				obj.turn,
				[] # TODO: references
				)
#}}}

class PostMessage( RequestHandler ):#{{{
	"""
	Request:  PostMessage :: Message
	Response: Okay | Fail
	"""
	def authorize( self, obj ):
		return True

	@MustBeLogged
	def __call__( self, request ):
		Container = self.game.objects.use( 'Board' )

		container = Container.ByID( request.id )

		if container:
			if self.authorize( container ):
				slot = request.slot if request.slot < len( container.messages ) else -1

				message = self.fromPacket( request ) 

				if slot == -1:
					container.messages.append( message )
				else:
					container.messages.insert( slot, message )

				with DatabaseManager().session() as session:
					session.add( container )

				if slot == -1:
					slot = len( container.messages )

				response = self.Okay( request, "Message posted on %s with id = %d in slot %d." % ( Container.__origname__, request.id, slot ) )
			else:
				msg( "${yel1}No permission for %s with id %s.${coff}" % ( Container.__origname__, request.id ) )
				response = self.Fail( request, "PermissionDenied", "You cannot access %s with id = %d." % ( Container.__origname__, request.id ) )
		else:
			msg( "${yel1}No such %s with id %s.${coff}" % ( Container.__origname__, request.id ) )
			response = self.Fail( request, "NoSuchThing", "No %s with id = %d." % ( Container.__origname__, request.id ) )

		return response 
#}}}

class GetMessage( GetWithIDSlotHandler, MessageFactoryMixin ):#{{{
	"""
	Request:  GetMessage :: GetWithIDSlot
	Response: Message | Sequence + (Message | Fail){2,n}
	"""
	__container__ = 'Board'

	def getItem( self, board, slot ):
		try:
			msg = None

			for message in board.messages:
				if message.id == slot:
					msg = message

			if not msg:
				return None
		except IndexError:
			return None
		else:
			msg.number = slot
			return msg
#}}}

class RemoveMessage( RemoveWithIDSlotHandler ):#{{{
	"""
	Request:  RemoveMessage :: GetMessage :: GetWithIDSlot
	Response: ( Okay | Fail ) | Sequence + ( Okay | Fail ){2,n}
	"""
	__container__ = 'Board'
#}}}

__all__ = [ 'PostMessage', 'GetMessage', 'RemoveMessage' ]
