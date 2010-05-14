from common import ConnectedTestSession

class CheckIfUserAuthorized( ConnectedTestSession ):
	description = "Checks if a server authorizes known user."

	def __iter__( self ):
		yield self.protocol.Login( self.seq, "test@tp", "test" )
