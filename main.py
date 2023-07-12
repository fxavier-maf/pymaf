import os

from utils.database_connector import DatabaseConnector

connection_info = { # pulled from vault
    "host": os.getenv("DBT_VERTICA_DEV_HOST"),
    "port": os.getenv("DBT_VERTICA_DEV_PORT"),
    "database": 'ca_dev',
    "user": os.getenv("DBT_VERTICA_DEV_USER"),
    "password": os.getenv("DBT_VERTICA_DEV_PASSWORD")
}


connection = DatabaseConnector(
    'vertica',
    loglevel='CRITICAL'
)

print("Connected to vertica")
# Connect to the Vertica database

# Execute a query
query = "SELECT * FROM ca_ods.ods_crf_dim_account limit 2"
df = connection.q(query)
print(df.shape)

df = connection.q(query)
print(df.shape)

