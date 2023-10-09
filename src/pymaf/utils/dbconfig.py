import pandas as pd

from .logger import pkg_logger as logger

class verticaConnection():
    def __init__(self, connection_info):
        self.connection_info = connection_info

    def connect(self):
        import vertica_python
        self.engine = vertica_python.connect(**self.connection_info)
        return self.engine



class sqlAlchemyDbConnection():
    """
    Manages connections to databases supported by core sqlalchemy package.
    """
    def __init__(self, db_type, connection_info):
        self.connection_info = connection_info
        dialect = {
            "postgresql": "postgresql",
            "mysql": "mysql+pymysql"
        }
        
        connection_prefix = dialect[db_type]
        if not connection_prefix:
            raise NotImplementedError(f"{db_type} is not implemented. Possible options: {','.join(dialect.keys())}")
        
        connection_info.update({'dialect': dialect.get(db_type)})
        self.connection_string = "{dialect}://{user}:{password}@{host}:{port}/{database}".format(**connection_info)
        logger.debug(f"Connection string : {self.connection_string}")

    def connect(self):
        try:
            from sqlalchemy import create_engine
            self.db_engine = create_engine(self.connection_string)
            return self.db_engine
        except (ConnectionError) as e:
            # logger.error("Error executing the query: {}".format(error))
            raise(e)

