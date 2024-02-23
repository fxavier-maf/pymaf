import os
import json
from datetime import datetime


import hvac
import getpass
# from hvac import exceptions


class Vault:
    def __init__(self, credentials_path="ldap-users/fxavier/config"):
        """
        Args:
            credentials_path: (str) Location of credentials on Vault
            https://vault.cicd.grid2.maf.ae
        """
        env_key = "DEVELOPER_ENVIRONMENT"
        environment = os.environ.get(env_key, "SANDBOX")
        supported_env_list = ["SANDBOX", "PRODUCTION", "RC"]
        if environment not in supported_env_list:
            raise NotImplementedError(f"{environment} is not authenticatable. Env should one of {','.join(supported_env_list)}")

        if not os.path.exists("tokens"):
            os.makedirs("tokens")

        self.environment = f"{environment}"
        self.url_key = f"{self.environment}_VAULT_URL"
        self.user_key = "MAF_USER"

        self.credentials_path = credentials_path
        self.vault_url = os.environ.get(self.url_key,
                                        'https://vault.cicd.grid2.maf.ae')

    def _get_vault_env_credentials(self):
        """
        Looks up environment variables to get vault credentials.

        Args:
            user: (str) Vault user for the above environment
            password: (str) Vault password for the above environment
        """
        user = os.environ.get(self.user_key)
        password = getpass.getpass(prompt="Enter MAF-AD password: ")
        return {"maf_ad_user": user, "maf_ad_password": password}

    def _read_token_from_disk(self, token_type="maf"):
        token_path = os.sep.join(["tokens", f"{token_type}_token.json"])
        token = None
        if os.path.exists(token_path):
            with open(token_path, "r") as file:
                token = json.load(file)

        return token

    def _validate_token(self, token):
        if not isinstance(token, dict):
            return False

        token_data = token.get('data', {})
        expiration_ts_string = token_data.get('expire_time')
        expiration_ts = datetime.strptime(expiration_ts_string[:23],
                                        '%Y-%m-%dT%H:%M:%S.%f')
        days_left = (expiration_ts - datetime.now()).days
        if days_left > 0:
            return token
        return False

    def _write_token_to_disk(self, token_type, token_content):
        token_path = os.sep.join(["tokens", f"{token_type}_token.json"])
        with open(token_path, "w") as file:
            json.dump(token_content, file)

    def get_client(self, auth_method="ldap"):
        """
        Creates an authenticated vault client.

        Args:
            auth_method: defaults to username & password.
        """
        try:
            self.client = hvac.Client(url=self.vault_url)

            # if unexpired token exists use that to extract credentials
            token = self._read_token_from_disk()
            is_valid_token = self._validate_token(token)
            if token and is_valid_token:
                self.client.token = token['data']['id']
                return self.client

            if auth_method == "ldap":
                credentials = self._get_vault_env_credentials()
                self.client.auth.ldap.login(
                    username=credentials["maf_ad_user"],
                    password=credentials["maf_ad_password"]
                )
            else:
                raise NotImplementedError(
                    f"Authentication with {auth_method} is not implemented"
                )

            # write retrieved token to disk for future 
            self._write_token_to_disk("maf",
                                      self.client.auth.token.lookup_self())
            return self.client
        except (hvac.exceptions.Forbidden,
                hvac.exceptions.Unauthorized,
                hvac.exceptions.InternalServerError,
                hvac.exceptions.InvalidRequest) as e:
            raise VaultCustomException(str(e))

    def _get_credentials(self):
        """
        Get credentials from the path provided by the user
        """
        response = self.get_client().secrets.kv.read_secret(path=self.credentials_path)
        if 'data' in response and response['data'] is not None:
            response = response['data']['data']

        return response

    def get_vertica_credentials(self):

        response = self._get_credentials()
        return {
            k.replace('maf-ad-', '').lower(): v
            for k, v
            in response.items()
            if k.startswith('maf')
        }


class VaultCustomException(Exception):
    pass

if __name__ == '__main__':
    x = Vault()
    c = x.get_client()
    print(c.is_authenticated())
    print(x.get_vertica_credentials())
