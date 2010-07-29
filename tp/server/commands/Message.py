#!/usr/bin/env python

from Common import FactoryMixin, RequestHandler, GetWithIDSlotHandler

class MessageFactoryMixin( FactoryMixin ):#{{{
	def toPacket( self, request, obj ):
		# FIXME: The reference system needs to be added and so does the turn
		Message = self.protocol.use( 'Message' )

		return Message( request._sequence,
				obj.board_id,
				obj.number,
				[],
				obj.subject,
				str( obj.body ),
				0,
				[] )
#}}}

class PostMessage( RequestHandler ):#{{{
	"""
	Request:  PostMessage :: Message
	Response: Okay | Fail
	"""
#}}}

class GetMessage( GetWithIDSlotHandler, MessageFactoryMixin ):#{{{
	"""
	Request:  GetMessage :: GetWithIDSlot
	Response: Message | Sequence + Message{2,n}
	"""
	__container__ = 'Board'

	def getItem( self, board, slot ):
		try:
			msg = board.messages[ slot ]
		except IndexError:
			return None
		else:
			msg.number = slot
			return msg
#}}}

class RemoveMessage( GetWithIDSlotHandler ):#{{{
	"""
	Request:  RemoveMessage :: GetMessage :: GetWithIDSlot
	Response: ( Okay | Fail ) | Sequence + ( Okay | Fail ){2,n}
	"""
	def __init__( self, *args, **kwargs ):
		GetWithIDSlotHandler.__init__( self, 'Slot', 'Message', *args, **kwargs )#}}}

__all__ = [ 'PostMessage', 'GetMessage', 'RemoveMessage' ]
