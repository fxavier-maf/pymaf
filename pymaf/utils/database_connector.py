import hashlib

import pandas as pd
import diskcache

from .dbconfig import verticaConnection, sqlAlchemyDbConnection
from .logger import pkg_logger as logger


class DatabaseConnector:
    """
    Creates an authenticated database connector, which can run queries
    and caches responses.

    Args:
        db_type: Option to select a database connection - vertica,postgres. Else raises Error.
        connection_info: Python dictionary containing host,user,password and port. Is ignored if auth_backend is set to Vault.
        auth_backend: Ignored if connection_info is not null. Else, use 'vault' or 'ini'.
        config_ini_path: Location of config.ini file.
        cache_timeout: timeouts in seconds
        cache_directory: Directory location
    """
    def __init__(self, db_type, auth_backend=None, connection_info={},
                 loglevel='DEBUG',
                 config_ini_path=None,
                 cache_directory=None,
                 cache_timeout=3600):
        self.db_type = db_type
        self.cache_enabled = True  # Flag to enable/disable caching
        self.cache = diskcache.Cache(directory=cache_directory if cache_directory else None,
                                    timeout=cache_timeout)

        if loglevel:
            logger.setLevel(level=loglevel.upper())

        if (not config_ini_path and not connection_info) and auth_backend != 'vault':
            raise TypeError("If Vault backend is not used, connection_info argument is expected.")

        # chooses connection parameters based on auth-backend
        if auth_backend == 'vault':
            from .vault import Vault # pragma: no cover
            self.connection_info = Vault().get_vertica_credentials() # pragma: no cover
        elif config_ini_path:
            from configparser import ConfigParser
            config = ConfigParser()
            config.read(config_ini_path)

            self.connection_info = {
                'user': config['vertica']['user'],
                'password': config['vertica']['password'],
                'dbname': config['vertica']['dbname'],
                'host': config['vertica']['host'],
                'port': int(config['vertica']['port']),
                'database': config['vertica']['database'],
                'connection_timeout': int(config['vertica']['connection_timeout'])
            }
        elif connection_info:
            self.connection_info = connection_info

        self.dbengine = None
        self.dbengine = self.connect()  # Placeholder for the database connection
 
    def connect(self):
        if self.dbengine is None:
            if self.db_type == 'vertica':
                self.connection_info.update(
                    {
                        'port': 5433,
                        'dbname': 'db1.data.maf.ae',
                        'database': 'CA_dev'
                    }
                )
                self.dbengine = verticaConnection(self.connection_info).connect()
            else:
                self.dbengine = sqlAlchemyDbConnection(self.connection_info).connect()

        return self.dbengine

    def q(self, query):
        cache_key = self._get_cache_key(query)

        try:
            result = self.cache.get(cache_key)
            if self.cache_enabled and result is not None:
                logger.debug("Returning cached query result.")
                return result

            result = pd.read_sql(query, self.dbengine)
            logger.debug("Query executed successfully!")

            if self.cache_enabled:
                self.cache.set(cache_key, result)

            return result
        except Exception as error:
            logger.error("Error executing the query: {}".format(error))

    def _get_cache_key(self, query):
        return hashlib.md5(query.encode()).hexdigest()

    # Enable/disable cache functionality
    def toggle_cache(self):
        self.cache_enabled = not self.cache_enabled
        logger.info("Caching enabled: {}".format(self.cache_enabled))

    def clear_cache(self):
        self.cache.clear()

    def close_connection(self):
        if self.dbengine is not None:
            self.dbengine.close()
            logger.debug("SQLAlchemy connection closed.")