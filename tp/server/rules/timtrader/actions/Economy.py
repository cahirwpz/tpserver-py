"""

for each resource 
	if not resource is factory:
		continue
	for each planets which have this factory type:

		mark factory as fully utilised

		for each production group:
			active = number of factories
			for each resource in requirement:
				if planet not has requirment:
					continue
				
				possible = planet[requirement[type]] / requirement[amount]
				if possible < active:
					active = possible

			for each resource in requirement:
				planet.remove_resource(active*requirement[amount])

			for each resource in production:
				planet.add_resource(active*production[amount])

			if group is "required":
				if active != number of factories:
					clear fully utilised counter...

				if active == zero:
					set non-utilised

		if factory is fully utilised: 
			increase the number of factories
		if factory is non-utilised:
			decrease the number of factories

Find all Factories which require no inputs.

"""

from tp.server.rules.timtrader.bases.Resource import Resource

def do():
	for rid in Resource.factories():
		r = Resource(rid)

		# Find all planets which have this resource.	
