import pecan
from pecan import rest, response

from lbaas.model import repositories as repo


def _loadbalancer_not_found():
    """Throw exception indicating container not found."""
    pecan.abort(404, 'Loadbalancer Not Found.')

class LoadbalancerController(object):
    def __init__(self, loadbalancer_id, loadbalancer_repo=None):
        self.loadbalancer_id = loadbalancer_id
        self.loadbalancer_repo = loadbalancer_repo or repo.LoadbalancerRepo()

    @pecan.expose(generic=True, template='json')
    def index(self):
        loadbalancer = self.loadbalancer_repo.get(
            entity_id=self.loadbalancer_id, keystone_id=1,
            suppress_exception=True)
        print 'ive returned from looking in the DB for a LB'

        if not loadbalancer:
            _loadbalancer_not_found()

        dict_fields = loadbalancer.to_dict()
        return dict_fields


class LoadbalancersController(object):
    @pecan.expose(generic=True, template='json')
    def _lookup(self, loadbalancer_id, *remainder):
        if loadbalancer_id:
            print 'Im in the lookup...'
            return LoadbalancerController(loadbalancer_id), remainder
