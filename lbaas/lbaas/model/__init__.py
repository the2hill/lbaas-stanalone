from pecan import conf

from lbaas.model import base
from sqlalchemy.ext import declarative
import sqlalchemy as sa
from sqlalchemy import orm


class LbaasBase(base.ModelBase):
    """Base class for Neutron Models."""
    __table_args__ = {'mysql_engine': 'InnoDB'}

    def __iter__(self):
        self._i = iter(orm.object_mapper(self).columns)
        return self

    def next(self):
        n = self._i.next().name
        return n, getattr(self, n)

    def __repr__(self):
        """sqlalchemy based automatic __repr__ method."""
        items = ['%s=%r' % (col.name, getattr(self, col.name))
                 for col in self.__table__.columns]
        return "<%s.%s[object at %x] {%s}>" % (self.__class__.__module__,
                                               self.__class__.__name__,
                                               id(self), ', '.join(items))

    def to_dict(self, exclude=None):
        exclude = exclude or []
        model_dict = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                model_dict[column.name] = getattr(self, column.name)
        return model_dict

    def to_dict_fields(self):
        created_at = self.created_at.isoformat() if self.created_at \
            else self.created_at

        updated_at = self.updated_at.isoformat() if self.updated_at \
            else self.updated_at

        """Returns a dictionary of just the db fields of this entity."""
        dict_fields = {'created': created_at,
                       'updated': updated_at,
                       'status': self.status}
        if self.deleted_at:
            dict_fields['deleted'] = self.deleted_at.isoformat()
        if self.deleted:
            dict_fields['is_deleted'] = True
        dict_fields.update(self._do_extra_dict_fields())
        return dict_fields

class HasTenant(object):
    """Tenant mixin, add to subclasses that have a tenant."""

    # NOTE(jkoelker) tenant_id is just a free form string ;(
    tenant_id = sa.Column(sa.String(255))


class HasId(object):
    """id mixin, add to subclasses that have an id."""

    id = sa.Column(sa.String(36),
                   primary_key=True,
                   default='default-generated-uuid-555-5555')


def init_model():
    """
    This is a stub method which is called at application startup time.

    If you need to bind to a parse database configuration, set up tables or
    ORM classes, or perform any database initialization, this is the
    recommended place to do it.

    For more information working with databases, and some common recipes,
    see http://pecan.readthedocs.org/en/latest/databases.html
    """


BASEV2 = declarative.declarative_base(cls=LbaasBase)



