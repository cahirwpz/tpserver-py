#!/usr/bin/env python

from tp.server.version import version as __version__

from Common import RequestHandler, MustBeLogged

class FinishedTurn( RequestHandler ):#{{{
	"""
	Request:  FinishedTurn
	Response: ?
	"""
#}}}

class GetTimeRemaining( RequestHandler ):#{{{
	"""
	Request:  GetTimeRemaining
	Response: TimeRemaining
	"""
	@MustBeLogged
	def __call__( self, request ):
		TimeRemaining = self.protocol.use( 'TimeRemaining' )

		return TimeRemaining( request._sequence, 0, 'Requested', 0, 'Bogus turn!' )
#}}}

class Connect( RequestHandler ):#{{{
	"""
	Request:  Connect
	Response: Okay | Fail | Redirect
	"""
	def __call__( self, request ):
		Okay, Fail, Redirect = self.protocol.use( 'Okay', 'Fail', 'Redirect' )

		version = ".".join(map(lambda i: str(i), __version__))

		return Okay( 0, "Welcome to tpserver-py %s!" % version )
#}}}

class Ping( RequestHandler ):#{{{
	"""
	Request:  Ping
	Response: Okay
	"""
	def __call__( self, request ):
		Okay = self.protocol.use( 'Okay' )

		return Okay( request._sequence, "PONG!")
#}}}

class GetFeatures( RequestHandler ):#{{{
	"""
	Request:  GetFeatures
	Response: Features
	"""
	def __call__( self, request ):
		Features = self.protocol.use( 'Features' )

		return Features( request._sequence,
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
#}}}

__all__ = [ 'FinishedTurn', 'GetTimeRemaining', 'Connect', 'Ping',
			'GetFeatures' ]
