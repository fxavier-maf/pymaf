from utils.dbconfig import verticaConnection, sqlAlchemyDbConnection
from utils.logger import pkg_logger as logger

class DatabaseConnector:
    def __init__(self, db_type, connection_info, loglevel='DEBUG'):
        self.db_type = db_type
        self.connection_info = connection_info

        logger.debug(self.connection_info)
        if loglevel:
            logger.setLevel(level=loglevel.upper())

    def connect(self):
        if self.db_type == 'vertica':
            self.dbengine = verticaConnection(self.connection_info)
        else:
            self.dbengine = sqlAlchemyDbConnection(self.connection_info)
        
        self.dbengine.connect()
        logger.info(f"Established connection as {self.connection_info['user']}")
        return self.dbengine

    def q(self, query):
        try:
            with self.connect() as connection:
                connection.execute(query)
            logger.debug("Query executed successfully!")
        except Exception as error:
            logger.error("Error executing the query: {}".format(error))
