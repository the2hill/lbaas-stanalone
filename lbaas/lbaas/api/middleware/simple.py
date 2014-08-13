from lbaas.api import middleware

# LOG = utils.getLogger(__name__)


class SimpleFilter(middleware.Middleware):

    def __init__(self, app):
        super(SimpleFilter, self).__init__(app)

    def process_request(self, req):
        """Just announce we have been called."""
        # LOG.debug("Calling SimpleFilter")
        return None