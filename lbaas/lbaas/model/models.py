from lbaas import model as models
from lbaas.common import constants

import sqlalchemy as sa
from sqlalchemy.ext import declarative
from sqlalchemy import orm
from sqlalchemy.orm import exc
from sqlalchemy.orm import validates

BASE = declarative.declarative_base()


class SessionPersistence(models.BASEV2):

    @declarative.declared_attr
    def __tablename__(cls):
        return "lbaas_sessionpersistence"

    pool_id = sa.Column(sa.String(36),
                        sa.ForeignKey("lbaas_pools.id"),
                        primary_key=True,
                        nullable=False)
    type = sa.Column(sa.Enum(*constants.SUPPORTED_SP_TYPES,
                             name="lbaas_sesssionpersistences_typev2"),
                     nullable=False)
    cookie_name = sa.Column(sa.String(1024), nullable=True)

    def to_dict(self, pool=False):
        sp_dict = super(SessionPersistence, self).to_dict(
            exclude=['pool_id'])
        if pool and self.pool:
            sp_dict['pool'] = self.pool.to_dict(members=True,
                                                listener=True,
                                                healthmonitor=True)
        return sp_dict


class Member(models.BASEV2, models.HasId, models.HasTenant):
    """Represents a load balancer member."""

    NAME = 'member'

    @declarative.declared_attr
    def __tablename__(cls):
        return "lbaas_members"

    __table_args__ = (
        sa.schema.UniqueConstraint('pool_id', 'address', 'protocol_port',
                                   name='uniq_pool_address_port_v2'),
    )
    pool_id = sa.Column(sa.String(36), sa.ForeignKey("lbaas_pools.id"),
                        nullable=False)
    address = sa.Column(sa.String(64), nullable=False)
    protocol_port = sa.Column(sa.Integer, nullable=False)
    weight = sa.Column(sa.Integer, nullable=True)
    admin_state_up = sa.Column(sa.Boolean(), nullable=False)
    subnet_id = sa.Column(sa.String(36), nullable=True)
    status = sa.Column(sa.String(16), nullable=False)

    def to_dict(self, pool=False):
        member_dict = super(Member, self).to_dict(exclude=['pool_id'])
        if pool and self.pool:
            member_dict['pool'] = self.pool.to_dict(members=True,
                                                    listener=True,
                                                    healthmonitor=True,
                                                    sessionpersistence=True)
        return member_dict

    def attached_to_loadbalancer(self):
        return bool(self.pool and self.pool.listener and
                    self.pool.listener.loadbalancer)


class HealthMonitor(models.BASEV2, models.HasId, models.HasTenant):
    """Represents a load balancer healthmonitor."""

    NAME = 'healthmonitor'

    @declarative.declared_attr
    def __tablename__(cls):
        return "lbaas_healthmonitors"

    type = sa.Column(sa.Enum(*constants.SUPPORTED_HEALTH_MONITOR_TYPES,
                             name="healthmonitors_typev2"),
                     nullable=False)
    delay = sa.Column(sa.Integer, nullable=False)
    timeout = sa.Column(sa.Integer, nullable=False)
    max_retries = sa.Column(sa.Integer, nullable=False)
    http_method = sa.Column(sa.String(16), nullable=True)
    url_path = sa.Column(sa.String(255), nullable=True)
    expected_codes = sa.Column(sa.String(64), nullable=True)
    status = sa.Column(sa.String(16), nullable=False)
    admin_state_up = sa.Column(sa.Boolean(), nullable=False)

    def to_dict(self, pool=False):
        hm_dict = super(HealthMonitor, self).to_dict()
        if pool and self.pool:
            hm_dict['pool'] = self.pool.to_dict(listener=True,
                                                members=True,
                                                sessionpersistence=True)
        return hm_dict

    def attached_to_loadbalancer(self):
        return bool(self.pool and self.pool.listener and
                    self.pool.listener.loadbalancer)


class Pool(models.BASEV2, models.HasId, models.HasTenant):
    """Represents a load balancer pool."""

    NAME = 'pool'

    @declarative.declared_attr
    def __tablename__(cls):
        return "lbaas_pools"

    name = sa.Column(sa.String(255), nullable=True)
    description = sa.Column(sa.String(255), nullable=True)
    healthmonitor_id = sa.Column(sa.String(36),
                                 sa.ForeignKey("lbaas_healthmonitors.id"),
                                 unique=True,
                                 nullable=True)
    protocol = sa.Column(sa.Enum(*constants.SUPPORTED_PROTOCOLS,
                                 name="pool_protocolsv2"),
                         nullable=False)
    lb_algorithm = sa.Column(sa.Enum(*constants.SUPPORTED_LB_ALGORITHMS,
                                     name="lb_algorithmsv2"),
                             nullable=False)
    admin_state_up = sa.Column(sa.Boolean(), nullable=False)
    status = sa.Column(sa.String(16), nullable=False)
    members = orm.relationship(Member,
                               backref=orm.backref("pool", uselist=False),
                               cascade="all, delete-orphan",
                               lazy='joined')
    healthmonitor = orm.relationship(
        HealthMonitor,
        backref=orm.backref("pool", uselist=False),
        lazy='joined')
    sessionpersistence = orm.relationship(
        SessionPersistence,
        uselist=False,
        backref=orm.backref("pool", uselist=False),
        cascade="all, delete-orphan",
        lazy='joined')

    def to_dict(self, members=False, healthmonitor=False, listener=False,
                sessionpersistence=True):
        pool_dict = super(Pool, self).to_dict()
        if members:
            member_list = self.members or []
            pool_dict['members'] = [member.to_dict()
                                    for member in member_list]
        if healthmonitor and self.healthmonitor:
            pool_dict['healthmonitor'] = self.healthmonitor.to_dict()
        if listener and self.listener:
            pool_dict['listener'] = self.listener.to_dict(loadbalancer=True)
        if sessionpersistence and self.sessionpersistence:
            pool_dict['session_persistence'] = (
                self.sessionpersistence.to_dict())
        return pool_dict

    def attached_to_loadbalancer(self):
        return bool(self.listener and self.listener.loadbalancer)


class LoadBalancer(models.BASEV2, models.HasId, models.HasTenant):
    """Represents a v2 neutron load balancer."""

    NAME = 'loadbalancer'

    @declarative.declared_attr
    def __tablename__(cls):
        return "lbaas_loadbalancers"

    name = sa.Column(sa.String(255))
    description = sa.Column(sa.String(255))
    vip_subnet_id = sa.Column(sa.String(36), nullable=False)
    vip_port_id = sa.Column(sa.String(36), nullable=True)
    # vip_port_id = sa.Column(sa.String(36), sa.ForeignKey('ports.id'))
    vip_address = sa.Column(sa.String(36))
    status = sa.Column(sa.String(16), nullable=False)
    admin_state_up = sa.Column(sa.Boolean(), nullable=False)
    # vip_port = orm.relationship(models.Port)
    # stats = orm.relationship(
    #     LoadBalancerStatistics,
    #     uselist=False,
    #     backref=orm.backref("loadbalancer", uselist=False),
    #     cascade="all, delete-orphan",
    #     lazy='joined')

    def to_dict(self, listeners=False, stats=False):
        lb_dict = super(LoadBalancer, self).to_dict()
        if listeners and self.listeners:
            lb_dict['listeners'] = [listener.to_dict(default_pool=True)
                                    for listener in self.listeners]
        if stats and self.stats:
            lb_dict['stats'] = self.stats.to_dict()
        return lb_dict


class Listener(models.BASEV2, models.HasId, models.HasTenant):
    """Represents a v2 neutron listener."""

    NAME = 'listener'

    @declarative.declared_attr
    def __tablename__(cls):
        return "lbaas_listeners"

    __table_args__ = (
        sa.schema.UniqueConstraint('loadbalancer_id', 'protocol_port',
                                   name='uniq_loadbalancer_listener_port'),
    )

    name = sa.Column(sa.String(255))
    description = sa.Column(sa.String(255))
    default_pool_id = sa.Column(sa.String(36), sa.ForeignKey("lbaas_pools.id"),
                                unique=True)
    loadbalancer_id = sa.Column(sa.String(36), sa.ForeignKey(
        "lbaas_loadbalancers.id"))
    protocol = sa.Column(sa.Enum(*constants.SUPPORTED_PROTOCOLS,
                                 name="listener_protocolsv2"),
                         nullable=False)
    protocol_port = sa.Column(sa.Integer, nullable=False)
    connection_limit = sa.Column(sa.Integer)
    admin_state_up = sa.Column(sa.Boolean(), nullable=False)
    status = sa.Column(sa.String(16), nullable=False)
    default_pool = orm.relationship(
        Pool, backref=orm.backref("listener", uselist=False), lazy='joined')
    loadbalancer = orm.relationship(
        LoadBalancer, backref=orm.backref("listeners"), lazy='joined')

    def to_dict(self, loadbalancer=False, default_pool=False):
        listener_dict = super(Listener, self).to_dict()
        if loadbalancer and self.loadbalancer:
            listener_dict['loadbalancer'] = self.loadbalancer.to_dict(
                listeners=True, stats=True)
        if default_pool and self.default_pool:
            listener_dict['default_pool'] = self.default_pool.to_dict(
                members=True, healthmonitor=True, sessionpersistence=True)
        return listener_dict

    def attached_to_loadbalancer(self):
        return bool(self.loadbalancer)

# Keep this tuple synchronized with the models in the file
MODELS = [Listener, LoadBalancer, HealthMonitor, Pool,
          Member, SessionPersistence]

def register_models(engine):
    """Creates database tables for all models with the given engine."""
    # LOG.debug("Models: {0}".format(repr(MODELS)))
    for model in MODELS:
        model.metadata.create_all(engine)


def unregister_models(engine):
    """Drops database tables for all models with the given engine."""
    for model in MODELS:
        model.metadata.drop_all(engine)