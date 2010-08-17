#!/usr/bin/env python

from Common import MustBeLogged, RequestHandler, GetWithIDHandler, GetWithIDSlotHandler, GetIDSequenceHandler, FactoryMixin

class OrderFactoryMixin( FactoryMixin ):
	def fromPacket( self, request ):
		Order = self.model.use( 'Order' )

		return None

	def toPacket( self, request, obj ):
		Order = self.protocol.use( 'Order' )

		return None

class OrderDescFactoryMixin( FactoryMixin ):
	def toPacket( self, request, obj ):
		OrderDesc = self.protocol.use( 'OrderDesc' )

		return None

class GetOrder( GetWithIDSlotHandler, OrderFactoryMixin ):
	"""
	Request:  GetOrder :: GetWithIDSlot
	Response: Order | Sequence + Order{2,n}
	"""
	__object__ = 'Order'

class GetOrderDesc( GetWithIDHandler, OrderDescFactoryMixin ):
	"""
	Request:  GetOrderDesc :: GetWithID
	Response: OrderDesc | Sequence + OrderDesc{2,n}
	"""

class GetOrderDescIDs( GetIDSequenceHandler ):
	"""
	Request:  GetOrderDescIDs :: GetIDSequence
	Response: IDSequence
	"""
	__packet__ = 'OrderDescIDs'
	__object__ = 'Order'

class OrderInsert( RequestHandler ):
	"""
	Request:  OrderInsert :: Order
	Response: Okay | Fail
	"""
	@MustBeLogged
	def __call__( self, request ):
		return request

class OrderProbe( RequestHandler ):
	"""
	Request:  OrderProbe :: Order
	Response: Order | Fail
	"""
	@MustBeLogged
	def __call__( self, request ):
		pass

class RemoveOrder( GetWithIDSlotHandler ):
	"""
	Request:  RemoveOrder :: GetWithIDSlot
	Response: ( Okay | Fail ) | Sequence + ( Okay | Fail ){2,n}
	"""

__all__ = [ 'GetOrder', 'GetOrderDesc', 'GetOrderDescIDs', 'OrderInsert',
			'OrderProbe', 'RemoveOrder' ]
