#!/usr/bin/env python

from Common import RequestHandler, GetWithIDSlotHandler

class MessageFactoryMixin( object ):#{{{
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
	__packet__    = 'Message'

	def getItem( self, board, slot ):
		try:
			return board.messages[ slot ]
		except IndexError:
			return None
#}}}

class RemoveMessage( GetWithIDSlotHandler ):#{{{
	"""
	Request:  RemoveMessage :: GetMessage :: GetWithIDSlot
	Response: ( Okay | Fail ) | Sequence + ( Okay | Fail ){2,n}
	"""
	def __init__( self, *args, **kwargs ):
		GetWithIDSlotHandler.__init__( self, 'Slot', 'Message', *args, **kwargs )#}}}

__all__ = [ 'PostMessage', 'GetMessage', 'RemoveMessage' ]
