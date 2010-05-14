from common import TestSession

class CheckSameSequenceInHeader( TestSession ):
	description = "Checks if a server drops second packet with same sequence."

	NoFailAllowed = False

	def __iter__( self ):
		yield self.protocol.Connect( 1, "tpserver-tests client" )
		yield self.protocol.Ping( 2 )
		packet = yield self.protocol.Ping( 2 )

		if packet._name == 'Okay':
			self.status = False
			self.reason = "Server does accept multiple packets with same sequence number!"
		else:
			self.status = True
