# pymaf

`pymaf` is a Python package designed to standardise everyday-boilerplate code in datascience use cases. It currently supports
simplifying database connectivity in a secure manner using Vault and disk-caching query results.

## Installation
To install `pymaf`, you can use pip with the GitHub repository URL. Run the following command in your terminal:

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

Authentication via Vault allows users to enter password once and run queries within an active session
for a minimum duration of 48 hours. Once the user enters their MAF-AD credentials, a Vault access token is 
generated that will be able to retrieve credentials from Vault and authenticate the user without intervention.

The setup is straightforward:
a. Please add your MAF-AD credentials to this location in Vault (Grid): `https://vault.cicd.grid2.maf.ae/ui/vault/secrets/secret/show/ldap-users/{MAF_USER}/config` under the
variable names : `maf-ad-username` and `maf-ad-password`. Please make sure to keep the variable names as-is.

b. Once this is done, use the following code to initiate connectivity:

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
```
