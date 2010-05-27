from tp.server.bases.Board     import Board
from tp.server.bases.Category  import Category
from tp.server.bases.Component import Component
from tp.server.bases.Design    import Design
from tp.server.bases.Game      import Game
from tp.server.bases.Message   import Message
from tp.server.bases.Object    import Object
from tp.server.bases.Order     import Order
from tp.server.bases.Property  import Property
from tp.server.bases.Resource  import Resource
from tp.server.bases.SQL       import NoSuchThing, PermissionDenied, SQLUtils
from tp.server.bases.User      import User

from tp.server import db

from tp.server.packet import PacketFactory

from version import version as __version__
from logging import msg

import inspect, time

class CommandsHandler( object ):
	def __init__( self, _module, _client ):
		self.objects = _module
		self._client = _client

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

		return commands

	def GetWithID( self, request, _type ):
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

		for _id in request.ids:
			try:
				obj = _type( _type.Utils.realid( self._client.user, _id ) )

				if _type.__name__ == 'User':
					_name = 'Player'
				else:
					_name = _type.__name__

				response.append( PacketFactory().fromObject( _name, request._sequence, obj ) )
			except PermissionDenied:
				msg( "${yel1}No permission for %s with id %s.${coff}" % ( _type, _id ) )
				response.append( self.objects.Fail( request._sequence, "PermissionDenied", "No %s." % _type, []) )
			except NoSuchThing:
				msg( "${yel1}No such %s with id %s.${coff}" % ( _type.__name__, _id ) )
				response.append( self.objects.Fail( request._sequence, "NoSuchThing", "No %s with id = %d." % (_type.__name__, _id), []) )

		return response
	
	def GetIDs( self, request, _type ):
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
		key   = long( _type.Utils.modified( self._client.user ).strftime('%s') )
		total = _type.Utils.amount( self._client.user )
		
		if request.key != -1 and key != request.key:
			return self.objects.Fail( request._sequence, "NoSuchThingThing", "Key %s is no longer valid, please get a new key." % request.key )
		
		if request._start + request._amount > total:
			msg( "Requested %d items starting at %d. Actually %s." % ( request._amount, request._amount, total ) )
			return self.objects.Fail( request._sequence, 'NoSuch', "Requested too many IDs. (Requested %s, Actually %s." % (request.start+request.amount, total))

		if request._amount == -1:
			left = 0
		else:
			left = total - ( request._start + request._amount )

		ids = _type.Utils.ids( self._client.user, request._start, request._amount )

		class Temp( object ):
			pass

		obj = Temp()
		obj.key		= key 
		obj.left	= left
		obj.ids		= sorted( (_id, int(time.mktime(time.strptime(_time.ctime())))) for _id, _time in ids )

		return PacketFactory().fromObject( _type.__name__ + "IDs", request._sequence, obj )
	
	def GetWithIDandSlot(self, request, _type, container):
		"""
		GetWithIDandSlot(request, type, container) -> [True | False]

		request - Get request to be processes, it must have the following
			request.id		- The id of the container
			request.slots	- The slots to be gotten
					
		type - The class used in processing, it must have the following
			type(realid, slot)                   - Creates the object
			typeinstance.to_packet(sequenceid)   - Creates a network packet with this sequence number

		container - The class that contains the other class
			container.realid(user, id)           - Get the real id for the container object
		"""
		response = []
		
		# Get the real id
		_id = container.Utils.realid( self._client.user, request.id )

		if len(request.slots) != 1:
			response.append( self.objects.Sequence( request._sequence, len( request.slots ) ) )

		for slot in request.slots:
			try:
				obj = _type( _id, slot )

				response.append( PacketFactory().fromObject( _type.__name__, request._sequence, obj ) )
			except PermissionDenied:
				msg( "${yel1}No permission for %s with id %s.${coff}" % ( _type, _id ) )
				response.append( self.objects.Fail( request._sequence, "PermissionDenied", "No %s." % _type, []) )
			except NoSuchThing:
				msg( "${yel1}No such %s with id %s.${coff}" % ( _type.__name__, _id ) )
				response.append( self.objects.Fail( request._sequence, "NoSuchThing", "No %s with id = %d." % (_type.__name__, _id), []) )

		return response

	def on_AddCategory( self, request ):
		pass

	def on_GetCategory( self, request ):
		return self.OnGetWithID( request, Category )

	def on_GetCategoryIDs( self, request ):
		return self.OnGetID( request, Category )

	def on_RemoveCategory( self, request ):
		pass

	def on_AddDesign( self, request ):
		pass

	def on_GetDesign( self, request ):
		return self.GetWithID( request, Design )

	def on_GetDesignIDs( self, request ):
		return self.GetIDs( request, Design )

	def on_ModifyDesign( self, request ):
		pass

	def on_RemoveDesign( self, request ):
		pass

	def on_GetBoards( self, request ):
		return self.GetWithID( request, Board )

	def on_GetBoardIDs( self, request ):
		return self.GetID( request, Board )

	def on_GetComponent( self, request ):
		return self.GetWithID( request, Component )

	def on_GetComponentIDs( self, request ):
		return self.GetIDs( request, Component )

	def on_GetObjectIDs( self, request ):
		return self.GetIDs( request, Object )	
	
	def on_GetObjectIDsByContainer( self, request ):
		pass

		# if not self.check( packet ):
		#	return True
		#
		# objects = Object.byparent(packet.id)
		#
		# return self.objects.Sequence(packet.sequence,)
	
	def on_GetObjectIDsByPos( self, request ):
		pass
	
	def on_GetObjectsByID( self, request ):
		# FIXME: This should show the correct number of orders for a certain person
		return self.GetWithID( request, Object )

	def on_GetObjectsByPos( self, request ):
		# if not self.check(packet):
		#	return True

		objs = Object.bypos( request._pos, request._size )
		
		response = [ self.objects.Sequence( request._sequence, len( objs ) ) ]
		response.extend( [ obj.to_packet( self._client.user, request._sequence ) for obj in objs ] )

		return response

	def on_GetOrder( self, request ):
		pass

	def on_GetGames( self, request ):
		ids = Game.ids()

		response = [ self.objects.Sequence(request.sequence, len(ids)) ]
		response.extend( Game(id).to_packet(request.sequence) for id, time in ids )

		return response

	def on_GetOrderDesc( self, request ):
		return self.GetWithIDandSlot( request, Order, Object )

	def on_GetOrderDescIDs( self, request ):
		pass

	def on_RemoveOrder( self, request ):
		pass

	def on_GetResource( self, request ):
		return self.GetWithID( request, Resource )
		
	def on_GetResourceIDs( self, request ):
		return self.GetIDs( request, Resource )

	def on_GetMessage( self, request ):
		return self.GetWithIDandSlot( request, Message, Board )

	def on_RemoveMessage( self, request ):
		pass

	def on_GetProperty( self, request ):
		return self.GetWithID( request, Property )

	def on_GetPropertyIDs( self, request ):
		return self.GetID( request, Property )
	
	def on_CreateAccount( self, request ):
		pass

	def on_GetPlayer( self, request ):
		return self.GetWithID( request, User )

	def on_FinishedTurn( self, request ):
		pass

	def on_GetTimeRemaining( self, request ):
		return self.objects.TimeRemaining( request._sequence, 0, 'Requested', 0, 'Bogus turn!' )

	def on_Login( self, request ):
		db.dbconn.use()

		try:
			username, game_name = User.Utils.split( request.username )
		except TypeError, ex:
			msg( "${yel1}%s${coff}" % ex, level="info" )

			return self.objects.Fail( request._sequence, "UnavailablePermanently", "Usernames should be of the form <username>@<game>!" )

		try:
			game = Game( shortname = game_name )
		except KeyError, ex:
			msg( "${yel1}%s${coff}" % ex, level="info" )

			return self.objects.Fail( request._sequence, "UnavailablePermanently",  "The game you specified is not valid!" )

		pid = User.Utils.usernameid( game, username, request.password )

		if pid == -1:
			return self.objects.Fail( request._sequence, "NoSuchThing", "Login incorrect or unknown username!" )
		else:
			self._client.user = User( id = pid )
			return self.objects.Okay( request._sequence, "Welcome user '%s' in game '%s'!" % ( username, game ) )

	def on_Connect( self, request ):
		version = ".".join(map(lambda i: str(i), __version__))
		return self.objects.Okay( 0, "Welcome to tpserver-py %s!" % version )

	def on_Ping( self, request ):
		return self.objects.Okay( request._sequence, "PONG!")

	def on_GetFeatures( self, request ):
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
