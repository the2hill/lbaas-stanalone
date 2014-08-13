from lbaas.api.controllers import loadbalancer
from lbaas.api.controllers import version


class RootController(object):
    v1 = version.VersionController()
    loadbalancers = loadbalancer.LoadbalancersController()
