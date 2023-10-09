import os

import hvac
# from hvac import exceptions

class Vault:
    def __init__(self, vault="secret/data/jupyterhub-development/config"):
        """
        Args:
            vault: (str) Location of credentials on path
        """
        env_key = "DEVELOPER_ENVIRONMENT"
        environment = os.environ.get(env_key, "SANDBOX")
        supported_env_list = ["SANDBOX", "PRODUCTION", "RC"]
        if environment not in supported_env_list:
            raise NotImplementedError(f"{environment} is not authenticatable. Env should one of {','.join(supported_env_list)}")

        self.environment = f"{environment}"
        self.url_key = f"{self.environment}_KEYSTORE_URL"
        self.user_key = f"{self.environment}_USER"
        self.password_key = f"{self.environment}_PASSWORD"

        self.credential_path = vault

    def _get_vault_env_credentials(self):
        """
        Looks up environment variables to get vault credentials.

        Required:
        1. DEVELOPER_ENVIRONMENT: expects values - sandbox, production or rc
        2. <ENV>_URL: Vault URL for the above environment (ex: SANDBOX_URL)
        3. <ENV>_USER: Vault user for the above environment (ex: SANDBOX_USER)
        4. <ENV>_PASSWORD: Vault password for the above environment (ex: SANDBOX_PASSWORD)
        """

        url = os.environ.get(self.url_key)
        user = os.environ.get(self.user_key)
        password = os.environ.get(self.password_key)

        return {"url": url, "user": user, "password": password}

    def get_client(self, auth_method="userpass"):
        """
        Creates an authenticated vault client.

        Args:
            auth_method: defaults to username & password.
        """
        try:
            credentials = self._get_vault_env_credentials()
            self.client = hvac.Client(url=credentials["url"])
            if auth_method == "userpass":
                self.client.auth.userpass.login(
                    username=credentials["user"], password=credentials["password"]
                )
            else:
                raise NotImplementedError(
                    f"Authentication with {auth_method} is not implemented"
                )

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
        response = self.get_client().read(self.credential_path)
        if 'data' in response and response['data'] is not None:
            response = response['data']['data']

        return response

    def get_vertica_credentials(self):
        response = self._get_credentials()
        return {k.replace('VERTICA_', '').lower(): v for k, v in response.items()}
    
class VaultCustomException(Exception):
    pass