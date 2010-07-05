from tp.server.bases import *
from tp.server.db import DatabaseManager

from tp.server.packet import PacketFactory, datetime2int

from version import version as __version__
from logging import msg
from gamemanager import GameManager
from sqlalchemy import *

import inspect

class CommandsHandler( object ):
	def __init__( self, _module, _client ):
		self.objects  = _module
		self.__client = _client

	@property
	def player( self ):
		return self.__client.player

	@property
	def game( self ):
		return self.__client.game

	def commands( self ):
		commands = []

		for name, method in inspect.getmembers( self, lambda o: inspect.ismethod(o) and o.__name__.startswith("on_" ) ):
			command = name.lstrip("on_")

			try:
				getattr( self.objects, command )
			except AttributeError:
				msg( "${yel1}Could not register handler method %s: unknown command %s.${coff}" % ( name, command ), level="warning" )
			else:
				commands.append( (command, method) )
		
		# available   = set( name for name in dir( self.objects ) if not name.startswith('_') )
		# implemented = set( cmd for cmd, method in commands )
		# print "Not implemented:", available.difference(implemented)

		return commands

	def GetWithID( self, request, Object ):
		"""
		GetWithID(request, type) -> [True | False]

		request - Get request to be processes, it must have the following
			request.ids - The ids to be gotten
					
		type - The class used in processing, it must have the following
			type(realid)                         - Creates the object
		"""
		response = []

		if len( request.ids ) > 1:
			response.append( self.objects.Sequence( request._sequence, len( request.ids ) ) )

		for obj_id in request.ids:
			try:
				obj = Object.ByRealId( self.player, obj_id )

				response.append( PacketFactory().fromObject( Object.__name__, request._sequence, obj ) )
			except PermissionDenied:
				msg( "${yel1}No permission for %s with id %s.${coff}" % ( Object.__name__, obj_id ) )
				response.append( self.objects.Fail( request._sequence, "PermissionDenied", "No %s." % Object.__name__, []) )
			except NoSuchThing:
				msg( "${yel1}No such %s with id %s.${coff}" % ( Object.__name__, obj_id ) )
				response.append( self.objects.Fail( request._sequence, "NoSuchThing", "No %s with id = %d." % (Object.__name__, obj_id), []) )

		return response
	
	def GetIDs( self, request, Object ):
		"""
		GetIDs(request, type) -> [True | False]

		request - Get request to be processes, it must have the following
			request.key    - The last modified time
			request.start  - Index to start from
			request.amount - The number of items to get
					
		type - The class used in processing, it must have the following
			type.modified(user)                 - Get the latest modified time for that type (that this user can see)
			type.amount(user)                   - Get the number of this that exist (that this user can see)
			type.ids(user, start, amount)       - Get the ids (that this user can see)
			type.ids_packet()                   - Get the packet type for sending a list of ids
		"""
		last  = Object.ByModTime( self.player )

		if last:
			key = long( last.mtime.strftime('%s') )
		else:
			key = -1

		total = Object.Count( self.player )
		
		if request.key != -1 and key != request.key:
			return self.objects.Fail( request._sequence, "NoSuchThing", "Key %s is no longer valid, please get a new key." % request.key )
		
		if request._start + request._amount > total:
			msg( "Requested %d items starting at %d. Actually %s." % ( request._amount, request._amount, total ) )
			return self.objects.Fail( request._sequence, 'NoSuch', "Requested too many IDs. (Requested %s, actually %s)" % (request._start + request._amount, total))

		if request._amount == -1:
			left = 0
		else:
			left = total - ( request._start + request._amount )

		objs = Object.ByIdRange( self.player, request._start, request._amount )

		class Temp( object ):
			pass

		obj = Temp()
		obj.key		= key 
		obj.left	= left
		obj.ids		= sorted( (obj.id, datetime2int( obj.mtime ) ) for obj in objs )

		return PacketFactory().fromObject( Object.__name__ + "IDs", request._sequence, obj )
	
	def GetWithIDandSlot(self, request, Slot, Object):
		"""
		GetWithIDandSlot(request, container, object) -> [True | False]

		request - Get request to be processes, it must have the following
			request.id		- The id of the container
			request.slots	- The slots to be gotten
		"""
		response = []
		
		if len( request.slots ) != 1:
			response.append( self.objects.Sequence( request._sequence, len( request.slots ) ) )

		for slot in request.slots:
			try:
				obj = Slot.ByIdAndNumber( request.id, slot )

				response.append( PacketFactory().fromObject( Object.__name__, request._sequence, obj.content ) )
			except PermissionDenied:
				msg( "${yel1}No permission for %s with id %s.${coff}" % ( Object.__name__, request.id ) )
				response.append( self.objects.Fail( request._sequence, "PermissionDenied", "No %s." % Object.__name__, []) )
			except NoSuchThing:
				msg( "${yel1}No such %s with id %s.${coff}" % ( Object.__name__, request.id ) )
				response.append( self.objects.Fail( request._sequence, "NoSuchThing", "No %s with id = %d." % (Object.__name__, request.id), []) )

		return response

	def on_AddCategory( self, request ):
		"""
		Request:  AddCategory :: Category
		Response: Category | Fail
		"""

	def on_GetCategory( self, request ):
		"""
		Request:  GetCategory :: GetWithID
		Response: Category | Sequence + Category{2,n}
		"""
		return self.GetWithID( request, self.game.Category )

	def on_GetCategoryIDs( self, request ):
		"""
		Request:  GetCategoryIDs :: GetIDSequence
		Response: IDSequence
		"""
		return self.GetIDs( request, self.game.Category )

	def on_RemoveCategory( self, request ):
		"""
		Request:  RemoveCategory :: GetCategory :: GetWithID
		Response: ( Okay | Fail ) | Sequence + ( Okay | Fail ){2,n}
		"""

	def on_AddDesign( self, request ):
		"""
		Request:  AddDesign :: Design
		Response: Design | Fail
		"""

	def on_GetDesign( self, request ):
		"""
		Request:  GetDesign :: GetWithID
		Response: Design | Sequence + Design{2,n}
		"""
		return self.GetWithID( request, self.game.Design )

	def on_GetDesignIDs( self, request ):
		"""
		Request:  GetDesignIDs :: GetIDSequence
		Response: IDSequence
		"""
		return self.GetIDs( request, self.game.Design )

	def on_ModifyDesign( self, request ):
		"""
		Request:  ModifyDesign :: Design
		Response: Design | Fail
		"""

	def on_RemoveDesign( self, request ):
		"""
		Request:  RemoveDesign :: GetDesign :: GetWithID
		Response: ( Okay | Fail ) | Sequence + ( Okay | Fail ){2,n}
		"""

	def on_GetBoards( self, request ):
		"""
		Request:  GetBoards :: GetWithID
		Response: Board | Sequence + Board{2,n}
		"""
		return self.GetWithID( request, self.game.Board )

	def on_GetBoardIDs( self, request ):
		"""
		Request:  GetBoardIDs :: GetIDSequence
		Response: IDSequence
		"""
		return self.GetID( request, self.game.Board )

	def on_GetComponent( self, request ):
		"""
		Request:  GetComponent :: GetWithID
		Response: Component | Sequence + Component{2,n}
		"""
		return self.GetWithID( request, self.game.Component )

	def on_GetComponentIDs( self, request ):
		"""
		Request:  GetComponentIDs :: GetIDSequence
		Response: IDSequence
		"""
		return self.GetIDs( request, self.game.Component )

	def on_GetObjectIDs( self, request ):
		"""
		Request:  GetObjectIDs :: GetIDSequence
		Response: IDSequence
		"""
		return self.GetIDs( request, self.game.Object )	
	
	def on_GetObjectIDsByContainer( self, request ):
		"""
		Request:  GetObjectIDsByContainer
		Response: IDSequence
		"""

		# if not self.check( packet ):
		#	return True
		#
		# objects = Object.byparent(packet.id)
		#
		# return self.objects.Sequence(packet.sequence,)
	
	def on_GetObjectIDsByPos( self, request ):
		"""
		Request:  GetObjectIDsByPos
		Response: IDSequence
		"""
	
	def on_GetObjectsByID( self, request ):
		"""
		Request:  GetObjectByID :: GetWithID
		Response: IDSequence
		"""
		# FIXME: This should show the correct number of orders for a certain person
		return self.GetWithID( request, self.game.Object )

	def on_GetObjectsByPos( self, request ):
		"""
		Request:  GetObjectsByPos
		Response: Object | Sequence + Object{2,n}
		"""
		objs = Object.bypos( request._pos, request._size )
		
		response = [ self.objects.Sequence( request._sequence, len( objs ) ) ]
		response.extend( [ obj.to_packet( self.player, request._sequence ) for obj in objs ] )

		return response

	def on_GetOrder( self, request ):
		"""
		Request:  GetOrder :: GetWithIDSlot
		Response: Order | Sequence + Order{2,n}
		"""

	def on_GetOrderDesc( self, request ):
		"""
		Request:  GetOrderDesc :: GetWithID
		Response: OrderDesc | Sequence + OrderDesc{2,n}
		"""
		return self.GetWithID( request, self.game.OrderDesc )

	def on_GetOrderDescIDs( self, request ):
		"""
		Request:  GetOrderDescIDs :: GetIDSequence
		Response: IDSequence
		"""

	def on_OrderInsert( self, request ):
		"""
		Request:  OrderInsert :: Order
		Response: Okay | Fail
		"""

	def on_OrderProbe( self, request ):
		"""
		Request:  OrderProbe :: Order
		Response: Order | Fail
		"""

	def on_RemoveOrder( self, request ):
		"""
		Request:  RemoveOrder :: GetWithIDSlot
		Response: ( Okay | Fail ) | Sequence + ( Okay | Fail ){2,n}
		"""

	def on_GetResource( self, request ):
		"""
		Request:  GetResource :: GetWithID
		Response: Resource | Sequence + Resource{2,n}
		"""
		return self.GetWithID( request, self.game.Resource )
		
	def on_GetResourceIDs( self, request ):
		"""
		Request:  GetResourceIDs :: GetIDSequence
		Response: IDSequence
		"""
		return self.GetIDs( request, Resource )

	def on_PostMessage( self, request ):
		"""
		Request:  PostMessage :: Message
		Response: Okay | Fail
		"""
		return PacketFactory().objects.Fail( request._sequence, 'NoSuchThing', 'Message adding failed.', [])

	def on_GetMessage( self, request ):
		"""
		Request:  GetMessage :: GetWithIDSlot
		Response: Message | Sequence + Message{2,n}
		"""
		return self.GetWithIDandSlot( request, self.game.Slot, self.game.Message )

	def on_RemoveMessage( self, request ):
		"""
		Request:  RemoveMessage :: GetMessage :: GetWithIDSlot
		Response: ( Okay | Fail ) | Sequence + ( Okay | Fail ){2,n}
		"""

	def on_GetProperty( self, request ):
		"""
		Request:  GetProperty :: GetWithID
		Response: Property | Sequence + Property{2,n}
		"""
		return self.GetWithID( request, self.game.Property )

	def on_GetPropertyIDs( self, request ):
		"""
		Request:  GetPropertyIDs :: GetIDSequence
		Response: IDSequence
		"""
		return self.GetID( request, Property )
	
	def on_CreateAccount( self, request ):
		"""
		Request:  CreateAccount
		Response: Okay | Fail
		"""

	def on_GetPlayer( self, request ):
		"""
		Request:  GetPlayer :: GetWithID
		Response: Player | Sequence + Player{2,n}
		"""
		return self.GetWithID( request, self.game.Player )

	def on_FinishedTurn( self, request ):
		"""
		Request:  FinishedTurn
		Response: ?
		"""

	def on_GetTimeRemaining( self, request ):
		"""
		Request:  GetTimeRemaining
		Response: TimeRemaining
		"""
		return self.objects.TimeRemaining( request._sequence, 0, 'Requested', 0, 'Bogus turn!' )

	def on_Login( self, request ):
		"""
		Request:  Login
		Response: Okay | Fail
		"""
		try:
			username, game_name = request.username.split('@', 1)
		except ValueError, ex:
			msg( "${yel1}%s${coff}" % ex, level="info" )

			return self.objects.Fail( request._sequence, "UnavailablePermanently", "Usernames should be of the form <username>@<game>!" )

		try:
			game = GameManager()[ game_name ]
		except KeyError, ex:
			msg( "${yel1}%s${coff}" % ex, level="info" )

			return self.objects.Fail( request._sequence, "UnavailablePermanently",  "The game you specified is not valid!" )

		player = game.Player.ByName( username, request.password )

		if player is not None:
			self.__client.game   = game
			self.__client.player = player 
			return self.objects.Okay( request._sequence, "Welcome user '%s' in game '%s'!" % ( username, game ) )
		else:
			return self.objects.Fail( request._sequence, "NoSuchThing", "Login incorrect or unknown username!" )

	def on_Connect( self, request ):
		"""
		Request:  Connect
		Response: Okay | Fail | Redirect
		"""
		version = ".".join(map(lambda i: str(i), __version__))
		return self.objects.Okay( 0, "Welcome to tpserver-py %s!" % version )

	def on_Ping( self, request ):
		"""
		Request:  Ping
		Response: Okay
		"""
		return self.objects.Okay( request._sequence, "PONG!")

	def on_GetFeatures( self, request ):
		"""
		Request:  GetFeatures
		Response: Features
		"""
		return self.objects.Features( request._sequence,
			[
				"AccountCreate",
				"DescBoardID",
				"DescCategoryID",
				"DescComponentID",
				"DescDesignID",
				"DescObjectID",
				"DescOrderID",
				"DescPropertyID",
				"DescResourceID",
				"KeepAlive",
				# "HTTPHere"
				# "HTTPThere"
				# "PropertyCalc"
				# "SecureHere"
				# "SecureThere"
			])
