"""
API application handler for Cloudkeep's Barbican
"""
import json

import pecan
from webob import exc as webob_exc

import lbaas.conf as cfg
db_config = dict(cfg.sqlalchemy)

from lbaas.api.controllers import loadbalancer


class JSONErrorHook(pecan.hooks.PecanHook):

    def on_error(self, state, exc):
        if isinstance(exc, webob_exc.HTTPError):
            exc.body = json.dumps({
                'code': exc.status_int,
                'title': exc.title,
                'description': exc.detail
            })
            state.response.content_type = "application/json"
            return exc.body


class PecanAPI(pecan.Pecan):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('hooks', []).append(JSONErrorHook())
        super(PecanAPI, self).__init__(*args, **kwargs)

    def route(self, req, node, path):
        # Pop the tenant ID from the path
        path = path.split('/')[1:]
        first_path = path.pop(0)

        path = '/%s' % '/'.join(path)
        controller, remainder = super(PecanAPI, self).route(req, node, path)

        # Pass the tenant ID as the first argument to the controller
        remainder = list(remainder)
        remainder.insert(0, first_path)
        return controller, remainder


def create_main_app(global_config, **local_conf):
    """uWSGI factory method for the LBaaS-API application."""

    class RootController(object):
        loadbalancer = loadbalancer.LoadbalancerController()

    wsgi_app = PecanAPI(RootController(), force_canonical=False)
    return wsgi_app