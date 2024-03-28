import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from utils.vault import Vault

@pytest.fixture
def vault(request):
    orig_value = os.environ['DEVELOPER_ENVIRONMENT']  # Default environment
    if hasattr(request, "param"):
        environment = request.param
        os.environ['DEVELOPER_ENVIRONMENT'] = environment

    yield Vault()
    os.environ['DEVELOPER_ENVIRONMENT'] = orig_value

def test_vault_lookup_keys_match_environment(vault):
    orig_value = os.environ['DEVELOPER_ENVIRONMENT']
    assert vault.environment == f"{orig_value}"
    assert vault.url_key == f"{orig_value}_VAULT_URL"
    assert vault.user_key == f"{orig_value}_MAF_USER"
    assert vault.password_key == f"{orig_value}_MAF_PASSWORD"

def test_vault_gets_credentials_dict(vault):
    response = vault._get_credentials()
    expected_type = dict
    assert isinstance(response, expected_type)
    assert response != {}

def test_vault_returns_usable_credentials(vault):
    expected_keys = ['host', 'user', 'password', 'port']
    response = vault.get_vertica_credentials()
    assert all(k in response for k in expected_keys)

def test_vault_raises_not_implemented_error():
    orig_value = os.environ['DEVELOPER_ENVIRONMENT']
    os.environ['DEVELOPER_ENVIRONMENT'] = 'local_env'
    
    with pytest.raises(NotImplementedError):
        Vault()
    
    os.environ['DEVELOPER_ENVIRONMENT'] = orig_value

def test_vault_raises_not_implemented_error_for_other_auth():
    with pytest.raises(NotImplementedError):
        Vault().get_client(auth_method='token')

# def test_vault_raises_error_for_incorrect_authentication():
#     from hvac import exceptions
#     os.environ['SANDBOX_PASSWORD'] = 'passwordpassword:P'
    
#     with pytest.raises(VaultCustomException):
#         Vault()    