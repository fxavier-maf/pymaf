import os

from database_connector import DatabaseConnector

connection_info = {
    "host": os.getenv("DBT_VERTICA_DEV_HOST"),
    "port": os.getenv("DBT_VERTICA_DEV_PORT"),
    "database": 'ca_dev',
    "user": os.getenv("DBT_VERTICA_DEV_USER"),
    "password": os.getenv("DBT_VERTICA_DEV_PASSWORD")
}
connection = DatabaseConnector(
    'vertica',
    connection_info
)

# Connect to the Vertica database
e = connection.connect()
print("Connected to vertica")

# Execute a query
query = "SELECT * FROM ca_ods.ods_crf_dim_account limit 2"
df = e.query(query)
print(df.shape)



# engine = maf_utils.Databaseconnector('vertica', connection_info)
# engine.query('select *from <table>')
# engine.cache = False