import sys
import webob.dec

# LOG = utils.getLogger(__name__)


class Middleware(object):
    """Base WSGI middleware wrapper. These classes require an application to be
    initialized that will be called next.  By default the middleware will
    simply call its wrapped app, or you can override __call__ to customize its
    behavior.
    """

    def __init__(self, application):
        self.application = application

    @classmethod
    def factory(cls, global_conf, **local_conf):
        def filter(app):
            return cls(app)
        return filter

    def process_request(self, req):
        """Called on each request.

        If this returns None, the next application down the stack will be
        executed. If it returns a response then that response will be returned
        and execution will stop here.

        """
        return None

    def process_response(self, response):
        """Do whatever you'd like to the response."""
        return response

    @webob.dec.wsgify
    def __call__(self, req):
        response = self.process_request(req)
        if response:
            return response
        response = req.get_response(self.application)
        response.request = req
        return self.process_response(response)


# Brought over from an OpenStack project
class Debug(Middleware):
    """Helper class that can be inserted into any WSGI application chain
    to get information about the request and response.
    """

    @webob.dec.wsgify
    def __call__(self, req):
        # LOG.debug(("*" * 40) + " REQUEST ENVIRON")
        for key, value in req.environ.items():
            # LOG.debug('{0}={1}'.format(key, value))
            pass
        # LOG.debug(' ')
        resp = req.get_response(self.application)

        # LOG.debug(("*" * 40) + " RESPONSE HEADERS")
        for (key, value) in resp.headers.iteritems():
            # LOG.debug('{0}={1}'.format(key, value))
            pass
        # LOG.debug(' ')

        resp.app_iter = self.print_generator(resp.app_iter)

        return resp

    @staticmethod
    def print_generator(app_iter):
        """Iterator that prints the contents of a wrapper string iterator
        when iterated.
        """
        # LOG.debug(("*" * 40) + " BODY")
        for part in app_iter:
            sys.stdout.write(part)
            sys.stdout.flush()
            yield part
        # LOG.debug(' ')