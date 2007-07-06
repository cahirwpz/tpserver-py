
from tp.server.db import *

from tp.server.bases.Resource  import Resource as ResourceBase

from tp.server.rules.timtrader.ProducersConsumers import split

class Resource(ResourceBase):
	attributes = { \
		'_products':     ResourceBase.Attribute('_products',        {}, 'private'),
		'transportable': ResourceBase.Attribute('transportable', False, 'private'),
	}

	def products_set(self, value):
		self._products = {}
		for requirements, output in value:
			self._products[str(requirements)] = str(output)
	def products_get(self):
		o = []
		for requirements, output in self._products.items():
			o.append((split(requirements), split(output)))
		return o
	products = property(products_get, products_set)

	def factory(self):
		return len(self._products) > 0
	factory = property(factory)

	# Get all resources which are transportable

	def transportables(cls):
		"""\
		ids([user, start, amount]) -> [id, ...]
		
		Get the last ids for this (that the user can see).
		"""
		te = cls.table_extra
		result = select([te.c.oid], (te.c.name=='transportable') & (te.c.value=='True')).execute().fetchall()
		return [x[0] for x in result]
	transportables = classmethod(transportables)
