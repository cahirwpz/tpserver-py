#! /usr/bin/env python

# This file checks you have installed the requirements for tpclient-pywx 
# It can be run as standalone but is also run by the client at startup

# Preference the local directory first...
import sys
sys.path.insert(0, '.')
import os.path

if os.path.exists("libtpproto-py"):
	sys.path.insert(0, "libtpproto-py")
if os.path.exists("schemepy"):
	sys.path.insert(0, "schemepy")

if os.path.exists(".git"):
	if os.path.exists("libtpproto-py") and not os.path.exists(os.path.join("libtpproto-py", "tp")) or \
	   os.path.exists("schemepy") and not os.path.exists(os.path.join("schemepy", "schemepy")):
		print "It appears this is a fresh git checkout, trying to get dependencies"
		os.system("git submodule init")
		os.system("git submodule update")
		print
		print


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
		if a <= b:
			continue
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

netlib_version = (0, 2, 2)
print
try:
	print " * Looking for Thousand Parsec Protocol Library,"
	import tp.netlib

	print "    Thousand Parsec Protocol Library Version", tp.netlib.__version__ 
	print "       (installed at %s)" % tp.netlib.__installpath__
	try:
		from tp.netlib.version import version_git
		print "       (git %s)" % version_git
	except ImportError:
		pass

	if not cmp(netlib_version, tp.netlib.__version__):
		raise ImportError("Thousand Parsec Network Library (libtpproto-py) is too old")

except Exception, e:
	print e
	notfound.append("tp.netlib > " + tostr(netlib_version))

print

sqlalchemy_version = (0, 4, 0)
try:
	print " * Looking for SQLAlchemy,"

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
try:
	print " * Looking for ElementTree implimentation,"

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
try:
	print " * Looking for SQLite,"

	import pysqlite2
	from pysqlite2 import dbapi2 as sqlite
	versions = list(sqlite.sqlite_version_info)+list(sqlite.version_info)
	print "      SQLite support installed, version %s.%s.%s (DPI version %s.%s.%s)" % tuple(versions)
except Exception, e:
	print e

	reason = "Installing sqlite is the smallest database supported."
	if system == "debian-based":
		recommended.append(("python-pysqlite2", reason))
	else:
		recommended.append(("pysqlite2", reason))

print
try:
	print " * Looking for MySQL support,"

	import MySQLdb
	print "      MySQL support installed, version", MySQLdb.__version__
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
		print e

		# Maybe it's using a different name
		import OpenSSL as pyOpenSSL
	print "      SSL support found, provided by", pyOpenSSL
except Exception, e:
	print e

	reason = "Installing pyOpenSSL allows encrypted connections."
	if system == "debian-based":
		recommended.append(("python-pyopenssl", reason))
	else:
		recommended.append(("pyOpenSSL", reason))

print
print 'Configuring Schemepy:'
print '---------------------------------------------------------------'
import os
import os.path
import re
import sys
if sys.platform.startswith('linux'):
	print ' * Checking mzscheme'
	cont = os.popen('mzscheme --version 2>/dev/null').read()
	if cont == '':
		print '    recommended package mzscheme not installed'
		print '    installing mzscheme can make the scheme part runs faster'
		if system == 'debian-based':
			print '    use "apt-get install plt-scheme" to install'
	else:
		mz_version = re.search(r'(MzScheme [^]]*\])', cont)
		if mz_version is None:
			print '    unknown mzscheme version: %s' % cont
		else:
			mz_version = mz_version.group(1)
			res = re.search(r'MzScheme v4.\d+.\d+ \[3m\]', mz_version)
			if res is None:
				print '    mzscheme >= v4 [3m] is needed, but got:'
				print '      %s' % mz_version
			else:
				print '    %s is installed' % mz_version
				if not os.path.exists('schemepy/schemepy/mzscheme/_mzhelper.so'):
					print '      mzhelper is not built, it is highly recommended to build it'
					print '      goto schemepy/schemepy/mzscheme and type "make" to build'
				else:
					print '      mzehlper is built, mzscheme backend should be available'
	print ' * Checking guile'
	cont = os.popen('guile --version 2>/dev/null').read()
	if cont == '':
		print '    recommended package guile not installed'
		print '    installing guile can make the scheme part runs faster'
		if system == 'debian-based':
			print '    use "apt-get install guile-1.8 guile-1.8-dev" to install'
	else:
		guile_version = re.search(r'(Guile (\d+).(\d+).\d+)', cont)
		if guile_version is None:
			print '    unknown guile version: %s' % cont
		else:
			gv_major, gv_minor = guile_version.group(2), guile_version.group(3)
			gv_major, gv_minor = int(gv_major), int(gv_minor)
			if gv_major >= 1 and gv_minor >= 6:
				print '      %s is installed' % guile_version.group(1)
				if not os.path.exists('schemepy/schemepy/guile/_guilehelper.so'):
					print '      guilehelper is not built, it is highly recommended to build it'
					print '      goto schemepy/schemepy/guile and type "make" to build'
				else:
					print '      guilehelper is built, guile backend should be available'
			else:
				print '      guile >= 1.6 is required, but got %s' % guile_version.group(1)
				
					  
else:
	print ' * Unknown OS, skip auto-checking'
print ' * Configuring load path for schemepy'
sys.path.append(os.path.abspath('./schemepy'))
print ' Done.'

print
print "Checking config file:"
print "---------------------------------------------------------------"

import os.path
if not os.path.exists('config.py'):
	print "WARNING: No config.py found, setting one up for you."
	import shutil
	shutil.copy('config.py-template', 'config.py')

import socket
try:
	import sys
	sys.path.insert(0, "/etc/tpserver-py")
	sys.path.insert(0, ".")
	import config

	config.dbconfig
	config.dbecho
	config.servername
	config.serverip
	config.socketecho
	config.metaserver

	print " * Configuration seems okay"
except socket.error, e:
	print e[1]
	print
	print "The config file was unable to figure out your hostname."
	print " Please set both 'serverip' and 'servername' values in config.py manually."
	sys.exit(1)
except AttributeError, e:
	print e
	print
	print "You seem to be missing a required configuration value."
	print " Please check the case and spelling of all values."
	sys.exit(1)
except Exception, e:
	print e
	print
	print "There is an unknown problem with your config file."
	print " Please check the file carefully."
	sys.exit(1)


if len(notfound) > 0 or len(recommended) > 0:
	print
	print "Possible problems found:"
	print "---------------------------------------------------------------"

if len(notfound) > 0:
	print "The following requirements where not met:"
	for module in notfound:
		print '    ', module
	print

import os, pprint
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
