#!/usr/bin/env python

from tp.server.bases import Object, Attribute

class Universe(Object):
	typeno = 0
	attributes = {'turn': Attribute('turn', 0, 'public')}

Object.types[Universe.typeno] = Universe
