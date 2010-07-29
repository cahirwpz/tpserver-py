
from tp.server.model import *

from tp.server.model import ResourceType as ResourceTypeBase

from tp.server.rules.timtrader.ProducersConsumers import split

class ResourceType( ResourceTypeBase ):
	#attributes = {
	#		'_products':     Attribute('_products',        {}, 'private'),
	#		'transportable': Attribute('transportable', False, 'private'),
	#		}

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

	@property
	def factory(self):
		return len(self._products) > 0

	# Get all resources which are transportable

	@classmethod
	def transportables(cls):
		te = cls.table_extra
		result = select([te.c.oid], (te.c.name=='transportable') & (te.c.value=='True')).execute().fetchall()
		return [x[0] for x in result]

	@classmethod
	def factories(cls):
		te = cls.table_extra
		result = select([te.c.oid], (te.c.name=='_products'), distinct=True).execute().fetchall()
		return [x[0] for x in result]
