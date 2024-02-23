# pymaf

`pymaf` is a Python package designed to simplify database interactions and improve efficiency with in-memory caching. It provides functionalities such as retrieving Vault-based credentials and using these credentials to authenticate database connections for running queries.

## Features

1. **Vault-based Credential Retrieval:** Securely retrieve your database credentials stored in Vault.
2. **Database Connection Authentication:** Use the retrieved credentials to authenticate your database connections.
3. **Query Caching on disk:** Improve your application's performance by caching query results on disk.

## Installation
To install `pymaf`, you can use pip with the GitHub repository. Run the following command in your terminal:

```bash
pip install git+https://github.com/fxavier-maf/pymaf.git
```


## Quick Start Guide

Here's a simple example of how to use `pymaf`:

### Database access

#### 1. using credentials from environment variables
```python
import os
from pymaf.utils.database_connector import DatabaseConnector

# Define your connection information
connection_info = {
    "host": os.getenv("VERTICA_DEV_HOST"),
    "port": os.getenv("VERTICA_DEV_PORT"),
    "database": 'ca_dev',
    "user": os.getenv("VERTICA_DEV_USER"),
    "password": os.getenv("VERTICA_DEV_PASSWORD")
}

# Establish a connection to your Vertica database
connection = DatabaseConnector('vertica', connection_info)

# Execute a query
query = "SELECT * FROM ca_ods.ods_crf_dim_account limit 2"
df = connection.q(query)

# The next time you run the same query, the data is fetched from cache if available.
df = connection.q(query)

# To disable caching, use the toggle_cache method:
connection.toggle_cache()
```

For more detailed information, please refer to the full documentation.


#### 2. using credentials from Vault

Authentication via Vault requires you to pass your MAF-AD credentials interactively (once).
Once the authentication is successful, the package will use the generated token to query
other credentials from Vault as required. Till token-expiry (2 days) or pod-inactivation
user do not need to supply their credentials again.

a. Please add your MAF-AD credentials to this location in Vault (Grid): `https://vault.cicd.grid2.maf.ae/ui/vault/secrets/secret/show/ldap-users/{MAF_USER}/config` under `maf-ad-username` and `maf-ad-password`.

b. Once this is done, use the following code to indicate your environment:

```python
import os
from pymaf.utils.database_connector import DatabaseConnector

# Establish a connection to your Vertica database
connection = DatabaseConnector('vertica', 'vault')

# During first login of the session, you will see the following prompt.
# Please enter your MAF-AD password:
# Enter MAF-AD password: 

# Execute a query
query = "SELECT * FROM ca_ods.ods_crf_dim_account limit 2"
df = connection.q(query)

# The next time you run the same query, the data is fetched from cache if available.
df = connection.q(query)

# To disable caching, use the toggle_cache method:
connection.toggle_cache()
```

For more detailed information, please refer to the full documentation.
