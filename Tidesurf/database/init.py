"""
This module contains the class to persist trades into SQLite
"""
import logging

from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import NoSuchModuleError
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.pool import StaticPool

from Tidesurf.exceptions import OperationalException
from Tidesurf.database.base import _DECL_BASE
from Tidesurf.database.model import Order, Trade, Cash
from Tidesurf.database.migrations import check_migrate

logger = logging.getLogger(__name__)


_SQL_DOCS_URL = 'http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls'


def init_db(db_url: str) -> Session:
    """
    Initializes this module with the given config,
    registers all known command handlers
    and starts polling for message updates
    :param db_url: Database to use
    :return: None
    """
    kwargs = {}

    if db_url == 'sqlite:///':
        raise OperationalException(
            f'Bad db-url {db_url}. For in-memory database, please use `sqlite://`.')
    if db_url == 'sqlite://':
        kwargs.update({
            'poolclass': StaticPool,
        })
    # Take care of thread ownership
    if db_url.startswith('sqlite://'):
        kwargs.update({
            'connect_args': {'check_same_thread': False},
        })

    try:
        engine = create_engine(db_url, future=True, **kwargs)
    except NoSuchModuleError:
        raise OperationalException(f"Given value for db_url: '{db_url}' "
                                   f"is no valid database URL! (See {_SQL_DOCS_URL})")

    # https://docs.sqlalchemy.org/en/13/orm/contextual.html#thread-local-scope
    # Scoped sessions proxy requests to the appropriate thread-local session.
    # We should use the scoped_session object - not a seperately initialized version
    Session = scoped_session(sessionmaker(bind=engine, autoflush=False))
    shared_session = Session()
    Trade._session = shared_session
    Order._session = shared_session
    Cash._session = shared_session
    Trade.query = Session.query_property()
    Order.query = Session.query_property()
    Cash.query = Session.query_property()
    previous_tables = inspect(engine).get_table_names()
    _DECL_BASE.metadata.create_all(engine)
    check_migrate(engine, decl_base=_DECL_BASE, previous_tables=previous_tables)
    return shared_session
