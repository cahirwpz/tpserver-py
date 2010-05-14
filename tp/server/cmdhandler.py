from tp.server.bases.Game   import Game
from tp.server.bases.User   import User
from tp.server.bases.Object import Object
from tp.server.bases.SQL    import NoSuch, PermissionDenied

from tp.server import db

from version import version as __version__
from logging import msg

import inspect

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
			type.realid(user, id)                - Get the real id for this object
			type(realid)                         - Creates the object
			typeinstance.to_packet(sequenceid)   - Creates a network packet with this sequence number
		"""
		response = []

		if len( request._ids ) > 1:
			response.append( self.objects.Sequence( request._sequence, len( request._ids ) ) )

		for _id in request._ids:
			try:
				obj = type( _type.realid( self._client.user, _id ) )
				response.append( obj.to_request( self._client.user, request._sequence ) )

			except PermissionDenied:
				msg( "${yel1}No permission for %s with id %s.${coff}" % ( _type, _id ) )
				response.append( self.objects.Fail( request._sequence, "NoSuch", "No such %s." % _type) )
			except NoSuch:
				msg( "${yel1}No such %s with id %s.${coff}" % ( _type, _id ) )
				response.append( self.objects.Fail( request._sequence, "NoSuch", "No such %s." % _type) )

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
		key   = long( _type.modified( self._client.user ).strftime('%s') )
		total = _type.amount( self._client.user )
		
		if request.key != -1 and key != request.key:
			return self.objects.Fail( request._sequence, "NoSuch", "Key %s is no longer valid, please get a new key." % request.key )
		
		if request._start + request._amount > total:
			msg( "Requested %d items starting at %d. Actually %s." % ( request._amount, request._amount, total ) )
			return self.objects.Fail( request._sequence, constants.FAIL_NOSUCH, "Requested to many IDs. (Requested %s, Actually %s." % (request.start+request.amount, total))

		if request._amount == -1:
			left = 0
		else:
			left = total - ( request._start + request._amount )

		ids = _type.ids( self._client.user, request._start, request._amount )

		return _type.id_packet()( request._sequence, key, left, ids)
	
	def OnGetWithIDandSlot(self, request, _type, container):
		"""\
		OnGetWithIDandSlot(request, type, container) -> [True | False]

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
		_id = container.realid( self._client.user, request._id )
		
		if len(request.slots) != 1:
			response.append( self.objects.Sequence( request._sequence, len( request._slots ) ) )

		for slot in request.slots:
			try:
				o = type(_id, slot)
				self._send(o.to_request(self._client.user, request.sequence))

			except PermissionDenied:
				msg( "No permission for %s with id %s." % (_type, _id) )

				self.objects.Fail( request._sequence, "NoSuch", "No such %s." % _type )
			except NoSuch:
				msg( "No such %s with id %s, %s." % (_type, _id, slot) )

				self.objects.Fail( request._sequence, "NoSuch", "No such order." )

		return True

	def on_AddCategory( self, request ):
		pass

	def on_GetCategory( self, request ):
		pass

	def on_GetCategoryIDs( self, request ):
		pass

	def on_RemoveCategory( self, request ):
		pass

	def on_AddDesign( self, request ):
		pass

	def on_GetDesign( self, request ):
		pass

	def on_GetDesignIDs( self, request ):
		pass

	def on_ModifyDesign( self, request ):
		pass

	def on_RemoveDesign( self, request ):
		pass

	def on_GetBoards( self, request ):
		pass

	def on_GetBoardIDs( self, request ):
		pass

	def on_GetComponent( self, request ):
		pass

	def on_GetComponentIDs( self, request ):
		pass

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

	def on_GetOrderDesc( self, request ):
		pass

	def on_GetOrderDescIDs( self, request ):
		pass

	def on_RemoveOrder( self, request ):
		pass

	def on_GetResource( self, request ):
		pass

	def on_GetResourceIDs( self, request ):
		pass

	def on_GetMessage( self, request ):
		pass

	def on_RemoveMessage( self, request ):
		pass

	def on_GetProperty( self, request ):
		pass

	def on_GetPropertyIDs( self, request ):
		pass
	
	def on_CreateAccount( self, request ):
		pass

	def on_GetPlayer( self, request ):
		pass

	def on_FinishedTurn( self, request ):
		pass

	def on_GetTimeRemaining( self, request ):
		pass

	def on_Login( self, request ):
		db.dbconn.use()

		try:
			username, game = User.split( request._username )
		except TypeError, ex:
			msg( "${yel1}%s${coff}" % ex, level="info" )

			return self.objects.Fail( request._sequence, "UnavailablePermanently", "Usernames should be of the form <username>@<game>!" )

		try:
			g = Game( shortname = game )
		except KeyError, ex:
			msg( "${yel1}%s${coff}" % ex, level="info" )

			return self.objects.Fail( request._sequence, "UnavailablePermanently",  "The game you specified is not valid!" )

		pid = User.usernameid( g, username, request._password )

		if pid == -1:
			return self.objects.Fail( request._sequence, "NoSuch", "Login incorrect or unknown username!" )
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
