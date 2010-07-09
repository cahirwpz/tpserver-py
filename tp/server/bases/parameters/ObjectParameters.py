#!/usr/bin/env python

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref

from tp.server.bases import SQLBase

ObjectParameters = [
	'Position3D',
	'Velocity3D',
	'Acceleration3D',
	'BoundPosition',
	'OrderQueue',
	'ResourceList',
	'Reference',
	'ReferenceQualityList',
	'Integer',
	'Size',
	'MediaUrl' ]

__all__ = []
