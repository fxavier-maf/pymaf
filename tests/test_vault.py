import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from pymaf.utils.vault import Vault

@pytest.fixture
def vault(request):
    yield Vault()

def test__get_vault_env_credentials(vault, monkeypatch):
    # Test _get_vault_env_credentials function

    def mock_getpass(prompt):
        return 'mocked_password'
    monkeypatch.setattr('getpass.getpass', mock_getpass)

    credentials = vault._get_vault_env_credentials()

    assert credentials['maf_ad_user'] == os.environ.get(vault.user_key)
    assert credentials['maf_ad_password'] == 'mocked_password'

def test_vault_gets_credentials_dict(vault):
    response = vault._get_credentials()
    expected_type = dict
    assert isinstance(response, expected_type)
    assert response != {}

def test_vault_returns_usable_credentials(vault):
    expected_keys = ['user', 'password']
    response = vault.get_vertica_credentials()
    assert all(k in response for k in expected_keys)
    assert all((k in response and response.get(k)) for k in expected_keys)

def test_vault_raises_not_implemented_error_for_other_auth():
    with pytest.raises(NotImplementedError):
        Vault().get_client(auth_method='token')