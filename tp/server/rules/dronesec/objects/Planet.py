from tp.server.rules.base.objects.Planet import Planet as PlanetBase

class Planet(PlanetBase):
  orderclasses = ('tp.server.rules.base.orders.NOp',
    'tp.server.rules.dronesec.orders.ProduceDrones')