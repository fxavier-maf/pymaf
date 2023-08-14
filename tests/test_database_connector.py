import os
import sys
import logging
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd

from utils.database_connector import DatabaseConnector

@pytest.fixture
def db_connector():
    # Create a DatabaseConnector instance with test configuration

    connection_info = {
        "host": os.getenv("DBT_VERTICA_DEV_HOST"),
        "port": os.getenv("DBT_VERTICA_DEV_PORT"),
        "database": 'ca_dev',
        "user": os.getenv("DBT_VERTICA_DEV_USER"),
        "password": os.getenv("DBT_VERTICA_DEV_PASSWORD")
    }
    db_connector = DatabaseConnector(db_type='vertica', connection_info=connection_info)
    yield db_connector
    # Clean up after the test
    db_connector.clear_cache()

def test_db_connector_init(db_connector):
    # Check if the db_connector is properly initialized
    assert db_connector.db_type == 'vertica'
    assert db_connector.cache_enabled is True
    assert db_connector.query_cache == {}

def test_db_connector_connect(db_connector):
    # Check if the connect() method establishes the database connection
    connection = db_connector.connect()
    assert connection is not None

def test_db_connector_q_with_cache(db_connector):
    # Check if the q() method retrieves query results from cache when cache is enabled
    query = "SELECT '22' as catch"
    cache_key = hashlib.md5(query.encode('utf-8')).hexdigest()
    expected_value = pd.DataFrame(['22'], columns=['catch'])
    
    db_connector.query_cache[cache_key] = expected_value
    db_connector.cache_enabled = True
    result = db_connector.q(query)
    assert result.values.tolist() == expected_value.values.tolist()

def test_db_connector_q_without_cache(db_connector):
    # Check if the q() method executes the query and caches the result when cache is enabled
    query = "SELECT '22' as catch"
    cache_key = hashlib.md5(query.encode('utf-8')).hexdigest()
    expected_value = pd.DataFrame(['22'], columns=['catch'])
    db_connector.cache_enabled = True

    result = db_connector.q(query)
    assert result.values.tolist() == expected_value.values.tolist()
    assert all(db_connector.query_cache[cache_key] == expected_value)

def test_db_connector_q_exception(db_connector, monkeypatch, caplog):
    # Check if the q() method logs an error when an exception occurs during query execution
    def mock_read_sql(query, dbengine):
        raise Exception('Query execution failed')
    
    monkeypatch.setattr('pandas.read_sql', mock_read_sql)
    
    with caplog.at_level(logging.ERROR):
        result = db_connector.q('SELECT 22')
        assert result is None
        assert 'Error executing the query' in caplog.text
        assert 'Query execution failed' in caplog.text

def test_db_connector_toggle_cache(db_connector):
    # Check if the toggle_cache() method enables/disables the cache functionality
    db_connector.toggle_cache()
    assert db_connector.cache_enabled is False
    db_connector.toggle_cache()
    assert db_connector.cache_enabled is True

def test_db_connector_clear_cache(db_connector):
    # Check if the clear_cache() method clears the query cache
    db_connector.query_cache['cache_key'] = 'cached_result'
    db_connector.clear_cache()
    assert db_connector.query_cache == {}

def test_db_connector_unsupported_auth_exception(db_connector):
    with pytest.raises(TypeError):
        db_connector = DatabaseConnector(db_type='vertica', connection_info={}, auth_backend='grid')