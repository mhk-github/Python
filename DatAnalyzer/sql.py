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


# Space efficient
class Source(Base):
    __tablename__ = 'sources'

    source_id = Column(
        Integer,
        Sequence(
            'sources_table_sequence',
            start=1,
            increment=1
        ),
        primary_key=True
    )

    source_name = Column(
        String(settings.MAX_SOURCE_NAME_LENGTH),
        nullable=False,
        unique=True
    )

    source_is_new = Column(
        Boolean,
        nullable=False,
        default=True
    )

    # One-to-many relationship with directories
    directories = relationship('Directory', cascade='all, delete-orphan')

    def __repr__(self):
        return (
            f"<Source: id={self.source_id}, name='{self.source_name}', "
            f"is_new={self.source_is_new}>"
        )


class Directory(Base):
    __tablename__ = 'directories'

    directory_id = Column(
        Integer,
        Sequence(
            'directories_table_sequence',
            start=1,
            increment=1
        ),
        primary_key=True
    )

    directory_name = Column(
        String(settings.MAX_DIRECTORY_NAME_LENGTH),
        nullable=False
    )

    # One-to-many relationship with files
    files = relationship('File', cascade='all, delete-orphan')

    # Foreign keys
    directory_parent_source_id = Column(
        Integer,
        ForeignKey('sources.source_id')
    )

    def __repr__(self):
        return (
            f"<Directory: id={self.directory_id}, name='{self.directory_name}'"
            f", source_id={self.directory_parent_source_id}>"
        )


class File(Base):
    __tablename__ = 'files'

    file_id = Column(
        Integer,
        Sequence(
            'files_table_sequence',
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

    # Foreign keys
    file_parent_directory_id = Column(
        Integer,
        ForeignKey('directories.directory_id')
    )

    def __repr__(self):
        return (
            f"<File: id={self.file_id}, name='{self.file_name}', "
            f"size={self.file_size}, mtime={self.file_mtime}, "
            f"directory_id={self.file_parent_directory_id}>"
        )


# Time efficient
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
