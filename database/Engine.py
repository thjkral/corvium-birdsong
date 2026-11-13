"""
Connect to the database and perform tasks
"""
import logging
from dataclasses import dataclass
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from database.tables import Recording_cleaned

class Engine:
    """
    Connector to the database using SQLAlchemy sessions
    """

    def __init__(self, config):
        self.user = config.user
        self.password = config.password
        self.database = config.database
        self.host = config.host
        self.port = config.port
        self.engine = self._generate_engine()

    def __str__(self):
        return f'User= {self.user}, Database= {self.database}'

    def _generate_engine(self):
        """
        Create a SQLAlchemy engine.
        """
        try:
            connection_string = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset=utf8mb4"
            engine = create_engine(connection_string,
                                   future=True,
                                   pool_pre_ping=True,
                                   pool_recycle=3600,
                                   )
            logging.info(f'Engine created successfully for database: {self.database}')
            return engine
        except Exception as err:
            logging.critical(f'Cannot create engine:\n{err}')
            exit(0)



