#! /usr/bin/env python

# This file checks you have installed the requirements for tpclient-pywx 
# It can be run as standalone but is also run by the client at startup

notfound    = []
recommended = []

# Try and figure out what type of system this computer is running.
import os
result = os.system('apt-get --version > /dev/null 2>&1') 
if result == 0:
	system = "debian-based"
elif result == 32512:
	system = "unknown"

from types import StringTypes
import re
def cmp(ver1, ver2):
	if type(ver2) in StringTypes:
		ver2 = [int(x) for x in ver2.split('.')]

	ver2 = list(ver2)
	for i,x in enumerate(ver2):
		try:
			ver2[i] = int(x)
		except ValueError:
			# This means there could be a "pre" or "rc" something in the version
			# We will treat this version as the one before.
			ver2[i] = int(re.search('(\d+)', x).group())-1

	for a, b in zip(ver1, ver2):
		if a <= b:
			continue
		return False
	return True

def tostr(ver1):
	s = ""
	for a in ver1:
		s += "."+str(a)
	return s[1:]

netlib_version = (0, 2, 2)
try:
	import tp.netlib
	print " * Thousand Parsec Protocol Library Version", tp.netlib.__version__
	if not cmp(netlib_version, tp.netlib.__version__):
		raise ImportError("Thousand Parsec Network Library (libtpproto-py) is too old")

except (ImportError, KeyError), e:
	notfound.append("tp.netlib > " + tostr(netlib_version))

try:
	import sqlalchemy
	print " * SQLAlchemy installed."
except (ImportError, KeyError), e:
	if system == "debian-based":
		notfound.append("python-sqlalchemy")
	else:
		notfound.append('SQLAlchemy')

try:
	import elementtree.ElementTree
	print " * Element Tree installed."
except (ImportError, KeyError), e:
	if system == "debian-based":
		notfound.append("python-elementtree")
	else:
		notfound.append("ElementTree")

import __builtin__
try:
	import gettext
	
	gettext.install("tpserver-py")
	__builtin__._ = gettext.gettext	
except ImportError, e:
	def _(s):
		return s
	__builtin__._ = _

	reason = "Without gettext support localisation will be disabled."
	if system == "debian-based":
		recommended.append(("Python gettext should come with Python, please check your python install", reason))
	else:
		recommended.append(("Python with gettext enabled.", reason))

try:
	import pysqlite2
	print " * SQLite support installed."
except ImportError, e:
	reason = "Installing sqlite is the smallest database supported."
	if system == "debian-based":
		recommended.append(("python-pysqlite2", reason))
	else:
		recommended.append(("pysqlite2", reason))

try:
	import MySQLdb
	print " * MySQL support installed."
except ImportError, e:
	reason = "A supported scalable database engine."
	if system == "debian-based":
		recommended.append(("python-mysql", reason))
	else:
		recommended.append(("Python MySQLdb", reason))

try:
	try:
		import pyOpenSSL
	except ImportError, e:
		# Maybe it's using a different name
		import OpenSSL as pyOpenSSL
	print " * Python OpenSSL support installed."
except ImportError, e:
	reason = "Installing pyOpenSSL allows encrypted connections."
	if system == "debian-based":
		recommended.append(("python-pyopenssl", reason))
	else:
		recommended.append(("pyOpenSSL", reason))

if len(notfound) > 0:
	print
	print "The following requirements where not met:"
	for module in notfound:
		print '\t', module

if len(recommended) > 0:
	print
	print "The following recommended modules where not found:"
	for module, reason in recommended:
		if len(module+',') > 16:
			i = '\t'
		else:
			i = '\t\t'
		print '\t', module + ',', i, reason

# Check for an apt-get based system,
if system == "debian-based":
	notfound_debian = []
	for module in notfound:
		if module.find(' ') == -1:
			notfound_debian.append(module)
	if len(notfound_debian) > 0:
		print """
You may be able to install some of the requirements by running the following
command as root:

	apt-get install %s
""" % " ".join(notfound_debian)
	if len(recommended) > 0:
		print """
To install the modules recommended for full functionality, run the following
command as root:
	apt-get install %s
""" % " ".join(zip(*recommended)[0])


if len(notfound) > 0:
	import sys
	sys.exit(1)
