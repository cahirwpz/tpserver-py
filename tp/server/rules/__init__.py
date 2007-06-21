
def rulesets():
	import os.path
	directory = os.path.dirname(__file__)

	rulesets = {}
	for entry in os.listdir(directory):
		fullentry = os.path.join(directory, entry)

		if os.path.isdir(fullentry):
			try:
				exec 'from %s import Ruleset as R' % entry
				R.path = entry
				rulesets[R.name] = R
			except ImportError, e:
				if str(e) == "cannot import name Ruleset":
					continue
				print e
	return rulesets

def prettyprint(ruleset):
	print "Name:\t\t%s (%s)"  % (ruleset.name, ruleset.path)
	print "Version:\t%s" % ruleset.version
	print ruleset.__doc__
