#!/usr/bin/env python

from Common import RequestHandler, GetWithIDHandler, GetWithIDSlotHandler, GetIDSequenceHandler

class GetOrder( GetWithIDSlotHandler ):#{{{
	"""
	Request:  GetOrder :: GetWithIDSlot
	Response: Order | Sequence + Order{2,n}
	"""
#}}}

class GetOrderDesc( GetWithIDHandler ):#{{{
	"""
	Request:  GetOrderDesc :: GetWithID
	Response: OrderDesc | Sequence + OrderDesc{2,n}
	"""
	def __init__( self, *args, **kwargs ):
		GetWithIDHandler.__init__( self, 'OrderDesc', *args, **kwargs )
#}}}

class GetOrderDescIDs( GetIDSequenceHandler ):#{{{
	"""
	Request:  GetOrderDescIDs :: GetIDSequence
	Response: IDSequence
	"""
#}}}

class OrderInsert( RequestHandler ):#{{{
	"""
	Request:  OrderInsert :: Order
	Response: Okay | Fail
	"""
#}}}

class OrderProbe( RequestHandler ):#{{{
	"""
	Request:  OrderProbe :: Order
	Response: Order | Fail
	"""
#}}}

class RemoveOrder( GetWithIDSlotHandler ):#{{{
	"""
	Request:  RemoveOrder :: GetWithIDSlot
	Response: ( Okay | Fail ) | Sequence + ( Okay | Fail ){2,n}
	"""
#}}}

__all__ = [ 'GetOrder', 'GetOrderDesc', 'GetOrderDescIDs', 'OrderInsert',
			'OrderProbe', 'RemoveOrder' ]
