

from tp.server.bases.Resource  import Resource as ResourceBase

from tp.server.rules.timtrader.ProducersConsumers import split

class Resource(ResourceBase):
	attributes = { \
		'_products': ResourceBase.Attribute('_products', {}, 'private'),
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
