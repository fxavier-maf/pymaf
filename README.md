# maf_utils

Currently, this package supports:

1. Retrieving Vault based credentials
2. Using supplied or looked up (Vault) credentials to authenticating DB connections to run queries
3. In-memory caching of queries.

  

Example usage:

```
import os
from utils.database_connector import DatabaseConnector

connection_info = {
    "host": os.getenv("VERTICA_DEV_HOST"),
    "port": os.getenv("VERTICA_DEV_PORT"),
    "database": 'ca_dev',
    "user": os.getenv("VERTICA_DEV_USER"),
    "password": os.getenv("VERTICA_DEV_PASSWORD")

}

# get vertica connection

connection = DatabaseConnector('vertica')

  

# Execute a query
query = "SELECT * FROM ca_ods.ods_crf_dim_account limit 2"
df = connection.q(query)

# Next time the query is run, the data is fetched from cache if available.
df = connection.q(query)

# To turn off cache, run:
connection.toggle_cache()
```