#! /usr/bin/env python3
# coding: utf-8
###############################################################################
# FILE     : sql.py
# SYNOPSIS : Utilities for databases.
# LICENSE  : MIT
# NOTE:
#    1. This is written for SQLite only.
###############################################################################


###############################################################################
# IMPORTS
###############################################################################

import logging
import reprlib

from pathlib import Path
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Sequence,
    String,
    create_engine,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
)
from sqlalchemy_utils import create_database
from typing import (
    List,
    TypeVar,
)

import settings


###############################################################################
# TYPING
###############################################################################

DatRecord = TypeVar('DatRecord')


###############################################################################
# CONSTANTS
###############################################################################

EMPTY_ID = 0


###############################################################################
# CLASSES
###############################################################################

Base = declarative_base()


class DatRecord(Base):
    __tablename__ = 'dats'

    dat_id = Column(
        Integer,
        Sequence(
            'dat_id_sequence',
            start=1,
            increment=1
        ),
        primary_key=True
    )

    file_name = Column(
        String(settings.MAX_FILE_NAME_LENGTH),
        nullable=False
    )

    file_size = Column(
        Integer,
        nullable=False
    )

    file_mtime = Column(
        DateTime,
        nullable=False
    )

    source_is_new = Column(
        Boolean,
        nullable=False,
        default=True
    )

    source_name = Column(
        String(settings.MAX_SOURCE_NAME_LENGTH),
        nullable=False,
    )

    directory_name = Column(
        String(settings.MAX_DIRECTORY_NAME_LENGTH),
        nullable=False
    )

    def __repr__(self):
        return (
            '<DatRecord: '
            f"dat_id={self.dat_id or EMPTY_ID}, "
            f"file_name='{self.file_name}', "
            f"file_size={self.file_size}, "
            f"file_mtime={int(self.file_mtime.timestamp())}, "
            f"source_is_new={int(self.source_is_new)}, "
            f"source_name='{self.source_name}', "
            f"directory_name='{self.directory_name}'"
            '>'
        )


###############################################################################
# FUNCTIONS
###############################################################################

def create_new_database(
        db: str,
        dat_list: List[DatRecord],
        show_sql: bool,
        indent: int = 2
) -> None:
    """Creates a new database.

    Parameters
    ----------
    db : str
        Name of the database to create
    dat_list : List[DatRecord]
        The DatRecord objects to add to the database
    show_sql : bool
        True is SQL output required
    indent : int
        Used for log formatting
    """

    logger = logging.getLogger(__name__)
    preamble = ' ' * indent
    logger.debug(
        f"{preamble}Enter create_new_database(db='{db}', "
        f"dat_list={reprlib.repr(dat_list)}, {show_sql=}, {indent=})"
    )

    # Delete existing SQLite3 database if necessary
    if db != ':memory:':
        p = Path(db)
        if p.is_file():
            p.unlink()
            logger.info(
                f"{preamble}  Deleted existing SQLite3 database '{db}'"
            )

    engine = create_engine(f"sqlite:///{db}", echo=show_sql)
    logger.info(f"{preamble}  Started database engine {engine}")

    if db != ':memory:':
        create_database(engine.url)
        logger.info(f"{preamble}    Created database '{engine.url}'")

    Base.metadata.create_all(engine)
    logger.info(f"{preamble}    Created all tables")

    # Add the data to the database
    logger.info(
        f"{preamble}    {len(dat_list)} items to add to database"
    )

    if dat_list:
        Session = sessionmaker(bind=engine)
        session = Session()
        logger.info(f"{preamble}    Session {session} started")

        current_start_index = 0
        current_limit_index = settings.BATCH_SIZE
        while True:
            data_slice = dat_list[current_start_index:current_limit_index]
            if data_slice:
                try:
                    session.bulk_save_objects(data_slice)
                    session.commit()
                    logger.info(
                        f"{preamble}      {len(data_slice)} items added"
                    )
                except IntegrityError as error:
                    logger.warning(
                        f"{preamble}      Integrity error:\n<<<{error}\n<<<"
                    )
                    session.rollback()
            else:
                break
            current_start_index = current_limit_index
            current_limit_index += settings.BATCH_SIZE

        logger.info(f"{preamble}    Session {session} ended")

    logger.info(f"{preamble}  Stopped database engine {engine}")
    logger.debug(f"{preamble}Leave create_new_database(...)")


###############################################################################
# END
###############################################################################
# Local Variables:
# mode: python
# End:
