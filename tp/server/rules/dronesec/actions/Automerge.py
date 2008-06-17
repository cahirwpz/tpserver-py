from tp.server.bases.Object import Object
from tp.server.rules.dronesec.objects.Fleet import Fleet
from tp.server.utils import WalkUniverse

def do(top):
	def h(obj):
		if obj.type == 'tp.server.rules.dronesec.objects.Fleet':
			#get all nearby fleets
			fleets = Object.bypos([obj.posx, obj.posy, obj.posz], size=0)
			fleets =  [id for (id, time) in fleets if Object(id).type == obj.type]

			for id in fleets:
				try:
					fleet = Object(id)
				except:
					print """This fleet has probably already been merged and
	the server hasn't updated itself yet"""
				#Make sure that the keys are the same (same types)
				#also makes sure that the ship isn't trying to merge with itself
				if fleet.ships.keys() == obj.ships.keys() and fleet.id != obj.id:
					# Merge the fleets have the same type of ships
					for type, number in fleet.ships.items():
						if obj.ships.has_key(type):
							obj.ships[type] += number
							fleet.ships[type] -= number
							#FIXME this will be printed at least twice
							print "Merging %s's %s with %s" % (obj.id, obj.ship_types[type], fleet.id)
					fleet.save()

			obj.save()
	WalkUniverse(top, "before",h)