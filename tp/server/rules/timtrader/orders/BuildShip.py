
from tp.server.bases import Object, Order, Message

from tp.server.rules.minisec.objects.Fleet import Fleet

class BuildFleet(Order):
	"""
	Build a new star ship from components at your head quaters.
	"""
	typeno = 2

	attributes = {
			'parts': Attribute("parts", {}, 'protected', type=netlib.objects.constants.ARG_LIST, 
				desc="Parts to build the ship from."),
			'name':  Attribute("name", 'New Fleet', 'protected', type=netlib.objects.constants.ARG_STRING, 
				desc="The new fleet's name.")
			}
	
	def do(self):
		builder = Object(self.oid)

		# FIXME: Check that this is a planet
		# FIXME: Check that this planet has the headquarter resource
		if False:
			print "Could not do a build order because it was on a planet headquaters. (This should not happen.)"
			self.remove()

		# Check that there are enough components to build this ship...
			
		# Build new fleet object
		fleet = Object(type='tp.server.rules.minisec.objects.Fleet')

		# Check if there is a design which matches this amount of components. If not create it...

		# Type Fleet
		fleet.parent = builder.id
		fleet.posx = builder.posx
		fleet.posy = builder.posy
		fleet.posz = builder.posz
		fleet.size = 1
		fleet.owner = builder.owner
		fleet.ships = self.ships
		fleet.insert()
		fleet.name = self.name
		fleet.save()

		message = Message()
		message.slot = -1
		message.bid = builder.owner
		message.subject = "Fleet built"
		
		message.body = """\
A new ship (%s) has been built and is orbiting %s.
""" % (fleet.name, builder.name)

		message.insert()

		self.remove()

	def resources(self):
		return self.parts.items()

	def fn_parts(self, value=None):
		cid = Category.byname('Ship Parts')

		if value == None:
			returns = []
			for rid in Resource.bycategory(cid)
				r = Resource(rid)
				returns.append((r.id, r.name, -1))
			return returns, self.parts.items()
		else:
			parts = {}

			for rid, number in value[1]:
				try:
					r = Resource(rid)
					if r.categories in cid:
						raise NoSuch()
				except NoSuch:
					raise ValueError("Invalid ship part selected.")
				parts[rid] = number

			self.parts = parts

	def fn_name(self, value=None):
		if value == None:
			return (255, self.name)
		else:
			self.name = value[1]

