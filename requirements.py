#! /usr/bin/env python

# This file checks you have installed the requirements for tpclient-pywx 
# It can be run as standalone but is also run by the client at startup

# Preference the local directory first...
import sys, os.path

sys.path.insert(0, '.')

modules = ["libtpproto2-py", "schemepy"]
for module in modules:
	if os.path.exists(module):
		sys.path.insert(0, module)

import tp.server.version as version

if hasattr(version, "version_git"):
	os.system("git submodule update --init")

notfound    = []
recommended = []

# Try and figure out what type of system this computer is running.
result = os.system('apt-get --version > /dev/null 2>&1') 

if result == 0:
	system = "debian-based"
elif result == 32512:
	system = "unknown"

from types import StringTypes
import re

def cmp(ver1, ver2):
	"""
	ver1 - required
	ver2 - actual
	"""
	if type(ver2) in StringTypes:
		ver2 = [int(re.sub('[^0-9].*','', x)) for x in ver2.split('.')]

	ver2 = list(ver2)
	for i,x in enumerate(ver2):
		try:
			ver2[i] = int(x)
		except ValueError:
			# This means there could be a "pre" or "rc" something in the version
			# We will treat this version as the one before.
			ver2[i] = int(re.search('(\d+)', x).group())-1

	for a, b in zip(ver1, ver2):
		if b > a:
			return True
		elif b == a:
			continue
		else:
			return False
		
	return True

def tostr(ver1):
	s = ""
	for a in ver1:
		s += "."+str(a)
	return s[1:]

print "My information:"
print "---------------------------------------------------------------"
from tp.server import version
try:
	print "My version", version.version_str+'+'+version.version_target_str, "(git %s)" % version.version_git
except AttributeError:
	print "My version", version.version_str
print "Running from ", os.path.dirname(os.path.join(os.path.abspath(__file__)))
print

print "Checking requirements:"
print "---------------------------------------------------------------"

netlib_version = (0, 4, 0)
print
try:
	print " * Looking for Thousand Parsec Protocol Library 2 Version,"
	import tp.netlib

	print "    Thousand Parsec Protocol Library 2 Version", tp.netlib.__version__ 
	print "       (installed at %s)" % tp.netlib.__installpath__
	try:
		from tp.netlib.version import version_git
		print "       (git %s)" % version_git
	except ImportError:
		pass

	if not cmp(netlib_version, tp.netlib.__version__):
		raise ImportError("Thousand Parsec Network Library 2 (libtpproto2-py) is too old")
except Exception, e:
	print e
	notfound.append("tp.netlib > " + tostr(netlib_version))

print

try:
	print " * Looking for ElementTree implementation,"

	ET = None
	errors = []
	try:
		import elementtree.ElementTree as ET
	except Exception, e:
		errors.append(e)
	try:
		import cElementTree as ET
	except Exception, e:
		errors.append(e)
	try:
		import lxml.etree as ET
	except Exception, e:
		errors.append(e)
	try:
		import xml.etree.ElementTree as ET
	except Exception, e:
		errors.append(e)

	if ET is None:
		raise ImportError(str(errors))

	print "    An Element Tree version is installed (%s)." % ET.__name__
except Exception, e:
	print e

	if system == "debian-based":
		notfound.append("python-elementtree")
	else:
		notfound.append("ElementTree")

print
import __builtin__
try:
	print " * Looking for gettext,"
	import gettext
	
	gettext.install("tpserver-py")
	__builtin__._ = gettext.gettext	
	print "    Found gettext."
except Exception, e:
	print e

	def _(s):
		return s
	__builtin__._ = _

	reason = "Without gettext support localisation will be disabled."
	if system == "debian-based":
		recommended.append(("Python gettext should come with Python, please check your python install", reason))
	else:
		recommended.append(("Python with gettext enabled.", reason))

print

twisted_version = (10, 1, 0)
try:
	print " * Looking for Twisted >= %s," % tostr(twisted_version)

	from twisted._version import version as twisted
	print "    Twisted installed, version %s" % twisted.base()

	twisted = ( twisted.major, twisted.minor, twisted.micro )

	if not cmp(twisted_version, twisted):
		raise ImportError("Twisted version %s is too old - %s needed." % (tostr(twisted_version), tostr(twisted)))
except Exception, e:
	print e

	if system == "debian-based":
		notfound.append("python-twisted-core")
	else:
		notfound.append("twisted")

print
sqlalchemy_version = (0, 6, 3)
try:
	print " * Looking for SQLAlchemy >= %s," % tostr(sqlalchemy_version)

	import sqlalchemy
	print "    SQLAlchemy installed version", sqlalchemy.__version__ 

	if not cmp(sqlalchemy_version, sqlalchemy.__version__):
		raise ImportError("SQLAlchemy version is too old")
except Exception, e:
	print e

	if system == "debian-based":
		notfound.append("python-sqlalchemy")
	else:
		notfound.append('SQLAlchemy')

print
sqlite_version = (3, 7, 2)
try:
	print " * Looking for SQLite >= %s," % tostr(sqlite_version)

	import pysqlite2
	from pysqlite2 import dbapi2 as sqlite
	versions = list(sqlite.sqlite_version_info)+list(sqlite.version_info)
	print "    SQLite support installed, version %s.%s.%s (DPI version %s.%s.%s)" % tuple(versions)

	if not cmp(sqlite_version, sqlite.sqlite_version_info):
		raise ImportError("SQLite version %s is too old - %s needed." % (tostr(sqlite.sqlite_version_info), tostr(sqlite_version)) )
except Exception, e:
	print e

	if system == "debian-based":
		notfound.append("python-pysqlite2")
	else:
		notfound.append("pysqlite2")

print
try:
	print " * Looking for MySQL support,"

	import MySQLdb
	print "    MySQL support installed, version", MySQLdb.__version__
except Exception, e:
	print e

	reason = "A supported scalable database engine."
	if system == "debian-based":
		recommended.append(("python-mysqldb", reason))
	else:
		recommended.append(("Python MySQLdb", reason))

print
try:
	print " * Looking for SSL support,"
	try:
		import pyOpenSSL
	except Exception, e:
		pass

	try:
		import OpenSSL as pyOpenSSL
	except Exception, e:
		pass

	pyOpenSSL.__version__

	print "    SSL support found, version", pyOpenSSL.__version__
except Exception, e:
	print e

	reason = "Installing pyOpenSSL allows encrypted connections."
	if system == "debian-based":
		recommended.append(("python-pyopenssl", reason))
	else:
		recommended.append(("pyOpenSSL", reason))

if len(notfound) > 0 or len(recommended) > 0:
	print
	print "Possible problems found:"
	print "---------------------------------------------------------------"

if len(notfound) > 0:
	print "The following requirements where not met:"
	for module in notfound:
		print '    ', module
	print

try:
	COLS = int(os.environ["COLUMNS"])
except (KeyError, ValueError):
	try:
		import struct, fcntl, sys, termios
		COLS = struct.unpack('hh', fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ, '1234'))[1]
	except:
		COLS = 80

ALIGN = 25
if len(recommended) > 0:
	print "The following recommended modules where not found:"
	for module, reason in recommended:
		
		lines = [""]
		lines[-1] += '    %s,' % module
		lines[-1] += ' ' * (ALIGN-len(lines[-1]))

		for word in reason.split(" "):
			if (len(lines[-1]) + len(word) + 1) > COLS:
				lines.append(' '*ALIGN)

			lines[-1] += word + " "

		print
		print "\n".join(lines)

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
