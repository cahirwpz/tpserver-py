#!/usr/bin/env python

from distutils.core import setup

import os.path
import os

setup(name="tpserver-py",
	version=(0, 1, 1),
	license="GPL",
	description="Python and SQL based Thousand Parsec server",
	author="Tim Ansell",
	author_email="tim@thousandparsec.net",
	url="http://www.thousandparsec.net",
	package_dir = {'': 'tp'},
	scripts=["tpserver-py", "tpserver-py-tool"],
	data_files=[('/etc/tpserver-py', ['config.py']),],
)
