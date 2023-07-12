from functools import lru_cache
from joblib import Memory
import hashlib

import pandas as pd

from .dbconfig import verticaConnection, sqlAlchemyDbConnection
from .logger import pkg_logger as logger

cache_directory = 'cache'
disk_cache = Memory(cache_directory)

class DatabaseConnector:
    def __init__(self, db_type, connection_info, loglevel='DEBUG', cache_directory='.cache'):
        self.db_type = db_type
        self.connection_info = connection_info
        self.cache_enabled = True  # Flag to enable/disable caching
        self.query_cache = {}  # Dictionary to store query results
        self.cache_directory = cache_directory
        self.disk_cache = disk_cache

        logger.debug(self.connection_info)
        if loglevel:
            logger.setLevel(level=loglevel.upper())
        
        self.dbengine = None
        self.dbengine = self.connect()  # Placeholder for the database connection
        
        
    def connect(self):
        if self.dbengine is None:
            if self.db_type == 'vertica':
                self.dbengine = verticaConnection(self.connection_info)
            else:
                self.dbengine = sqlAlchemyDbConnection(self.connection_info)
        
            # logger.info(f"Established connection as {self.connection_info['user']}")
        return self.dbengine.connect()

    # todo; enable getting login details from Vault
    def q(self, query):
        cache_key = self._get_cache_key(query)
        if self.cache_enabled and cache_key in self.query_cache:
            logger.debug("Returning cached query result.")
            return self.query_cache[cache_key]

        try:
            result = pd.read_sql(query, self.dbengine)
            logger.debug("Query executed successfully!")
            if self.cache_enabled:
                self.query_cache[cache_key] = result
            return result
        except Exception as error:
            logger.error("Error executing the query: {}".format(error))

    def _get_cache_key(self, query):
        return hashlib.md5(query.encode()).hexdigest()
    
    # Enable/disable cache functionality
    def enable_cache(self):
        self.cache_enabled = True

    def disable_cache(self):
        self.cache_enabled = False

    def is_cache_enabled(self):
        return self.cache_enabled

    def clear_cache(self):
        self.query_cache.clear()