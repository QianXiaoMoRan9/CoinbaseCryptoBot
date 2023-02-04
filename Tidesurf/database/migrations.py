import logging

from sqlalchemy import text

logger = logging.getLogger(__name__)


def set_sqlite_to_wal(engine):
    if engine.name == 'sqlite' and str(engine.url) != 'sqlite://':
        # Set Mode to
        with engine.begin() as connection:
            connection.execute(text("PRAGMA journal_mode=wal"))


def check_migrate(engine, decl_base, previous_tables) -> None:
    """
    Checks if migration is necessary and migrates if necessary
    """
    set_sqlite_to_wal(engine)
