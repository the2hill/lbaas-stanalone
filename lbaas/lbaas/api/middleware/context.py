import json
import webob.exc

from lbaas.api import middleware as mw

import lbaas.context


# LOG = utils.getLogger(__name__)

class BaseContextMiddleware(mw.Middleware):
    def process_response(self, resp):
        try:
            request_id = resp.request.context.request_id
        except AttributeError:
            # LOG.warn(u._('Unable to retrieve request id from context'))
            pass
        else:
            resp.headers['x-openstack-request-id'] = 'req-%s' % request_id
        return resp


class ContextMiddleware(BaseContextMiddleware):
    def __init__(self, app):
        # self.policy_enforcer = policy.Enforcer()
        super(ContextMiddleware, self).__init__(app)

    def process_request(self, req):
        """Convert authentication information into a request context

        Generate a lbaas.context.RequestContext object from the available
        authentication headers and store on the 'context' attribute
        of the req object.

        :param req: wsgi request object that will be given the context object
        :raises webob.exc.HTTPUnauthorized: when value of the X-Identity-Status
                                            header is not 'Confirmed' and
                                            anonymous access is disallowed
        """
        if req.headers.get('X-Identity-Status') == 'Confirmed':
            req.context = self._get_authenticated_context(req)
        else:
            req.context = self._get_anonymous_context()
            # raise webob.exc.HTTPUnauthorized()

        # Ensure that down wind mw.Middleware/app can see this context.
        req.environ['lbaas.context'] = req.context

    def _get_anonymous_context(self):
        kwargs = {
            'user': None,
            'tenant': None,
            'roles': [],
            'is_admin': False,
            'read_only': True,
            'policy_enforcer': self.policy_enforcer,
        }
        return lbaas.context.RequestContext(**kwargs)

    def _get_authenticated_context(self, req):
        #NOTE(bcwaldon): X-Roles is a csv string, but we need to parse
        # it into a list to be useful
        roles_header = req.headers.get('X-Roles', '')
        roles = [r.strip().lower() for r in roles_header.split(',')]

        #NOTE(bcwaldon): This header is deprecated in favor of X-Auth-Token
        #(mkbhanda) keeping this just-in-case for swift
        deprecated_token = req.headers.get('X-Storage-Token')

        service_catalog = None
        if req.headers.get('X-Service-Catalog') is not None:
            try:
                catalog_header = req.headers.get('X-Service-Catalog')
                service_catalog = json.loads(catalog_header)
            except ValueError:
                raise webob.exc.HTTPInternalServerError(
                    u._('Invalid service catalog json.'))

        kwargs = {
            'user': req.headers.get('X-User-Id'),
            'tenant': req.headers.get('X-Tenant-Id'),
            'roles': roles,
            'is_admin': True,
            'auth_tok': req.headers.get('X-Auth-Token', deprecated_token),
            'owner_is_tenant': True,
            'service_catalog': service_catalog,
            'policy_enforcer': self.policy_enforcer,
        }

        return lbaas.context.RequestContext(**kwargs)


class UnauthenticatedContextMiddleware(BaseContextMiddleware):
    def process_request(self, req):
        """Create a context without an authorized user."""
        kwargs = {
            'user': None,
            'tenant': None,
            'roles': [],
            'is_admin': True,
        }

        req.context = lbaas.context.RequestContext(**kwargs)