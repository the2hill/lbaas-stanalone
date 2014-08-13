"""
Interace to the Alembic migration process and environment.

Concepts in this file are based on Quantum's Alembic approach.

Available Alembic commands are detailed here:
https://alembic.readthedocs.org/en/latest/api.html#module-alembic.command
"""

import os

from alembic import command as alembic_command
from alembic import config as alembic_config

import lbaas.conf as cfg
db_opts = dict(cfg.sqlalchemy)

# LOG = utils.getLogger(__name__)


def init_config(sql_url=None):
    """Initialize and return the Alembic configuration."""
    sqlalchemy_url = db_opts['sql_connection']

    config = alembic_config.Config(
        os.path.join(os.path.dirname(__file__), 'alembic.ini')
    )
    config.barbican_sqlalchemy_url = sqlalchemy_url
    config.set_main_option('script_location',
                           'lbaas.model.migration:alembic_migrations')
    return config


def upgrade(to_version='head', sql_url=None):
    """Upgrade to the specified version."""
    alembic_cfg = init_config(sql_url)
    if alembic_cfg:
        alembic_command.upgrade(alembic_cfg, to_version)


def downgrade(to_version, sql_url=None):
    """Downgrade to the specified version."""
    alembic_cfg = init_config(sql_url)
    if alembic_cfg:
        alembic_command.downgrade(alembic_cfg, to_version)


def stamp(to_version='head', sql_url=None):
    """Stamp the specified version, with no migration performed."""
    alembic_cfg = init_config(sql_url)
    if alembic_cfg:
        alembic_command.stamp(alembic_cfg, to_version)


def generate(autogenerate=True, message='generate changes', sql_url=None):
    """Generate a version file."""
    alembic_cfg = init_config(sql_url)
    if alembic_cfg:
        alembic_command.revision(alembic_cfg, message=message,
                                 autogenerate=autogenerate)