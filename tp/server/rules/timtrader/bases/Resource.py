

from tp.server.bases.Resource  import Resource as ResourceBase

class Resource(ResourceBase):
	attributes = { \
		'products': ResourceBase.Attribute('products', [], 'public'),
	}
