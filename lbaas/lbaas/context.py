import random


class RequestContext(object):
    """Stores information about the security context under which the user
    accesses the system, as well as additional request information.
    """

    def __init__(self, auth_tok=None, user=None, tenant=None, roles=None,
                 is_admin=False, read_only=False, show_deleted=False,
                 owner_is_tenant=True, service_catalog=None,
                 policy_enforcer=None):
        self.auth_tok = auth_tok
        self.user = user
        self.tenant = tenant
        self.roles = roles or []
        self.read_only = read_only
        self.owner_is_tenant = owner_is_tenant
        self.request_id = random.randint()
        self.service_catalog = service_catalog
        self.policy_enforcer = policy_enforcer
        self.is_admin = is_admin


    def to_dict(self):
        return {
            'request_id': self.request_id,
            'user': self.user,
            'user_id': self.user,
            'tenant': self.tenant,
            'tenant_id': self.tenant,
            'project_id': self.tenant,
            'roles': self.roles,
            'auth_token': self.auth_tok,
            'service_catalog': self.service_catalog,
        }

    @classmethod
    def from_dict(cls, values):
        return cls(**values)

    def update_store(self):
        # local.store.context = self
        pass

    @property
    def owner(self):
        """Return the owner to correlate with key."""
        return self.tenant if self.owner_is_tenant else self.user