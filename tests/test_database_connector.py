import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd

from pymaf.utils.database_connector import DatabaseConnector

@pytest.fixture
def db_connector():
    # Create a DatabaseConnector instance with test configuration

    connection_info = {
        "host": os.getenv("VERTICA_HOST"),
        "port": os.getenv("VERTICA_PORT"),
        "database": 'ca_dev',
        "user": os.getenv("VERTICA_USER"),
        "password": os.getenv("VERTICA_PASSWORD")
    }
    db_connector = DatabaseConnector(db_type='vertica', connection_info=connection_info)
    yield db_connector


def test_db_connector_init(db_connector):
    # Check if the db_connector is properly initialized
    assert db_connector.db_type == 'vertica'
    assert db_connector.cache_enabled is True


def test_db_connector_connect(db_connector):
    # Check if the connect() method establishes the database connection
    connection = db_connector.connect()
    assert connection is not None


def test_db_connector_q_with_cache(db_connector):
    # Check if the q() method retrieves query results from cache when cache is enabled
    query = "SELECT '22' as catch"
    cache_key = db_connector._get_cache_key(query)
    expected_value = pd.DataFrame(['22'], columns=['catch'])

    db_connector.cache_enabled = True
    _ = db_connector.q(query)

    assert len(list(db_connector.cache.iterkeys())) == 1
    assert db_connector.cache.pop(cache_key).equals(expected_value)
    db_connector.clear_cache()


def test_db_connector_q_without_cache(db_connector):
    # Check if the q() method executes the query and caches the result when cache is enabled
    query = "SELECT '22' as catch"
    db_connector.cache_enabled = False

    _ = db_connector.q(query)
    assert len(list(db_connector.cache.iterkeys())) == 0


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
    assert len(list(db_connector.cache.iterkeys())) == 0
    db_connector.cache.add('cache_key', 'cached_result')
    assert len(list(db_connector.cache.iterkeys())) == 1
    db_connector.clear_cache()
    assert len(list(db_connector.cache.iterkeys())) == 0


# def test_connection_closure(db_connector):
#     # tests that None is returned when closed connection is called for querying
#     db_connector.close_connection()
#     with pytest.raises(Exception):
#         _ = db_connector.q("select 22")


# def test_db_connector_unsupported_auth_exception():
#     with pytest.raises(TypeError):
#         DatabaseConnector(db_type='vertica', connection_info={}, auth_backend='grid')


# def test_db_connector_config_ini_input():
#     with pytest.raises(TypeError):
#         DatabaseConnector(db_type='vertica', config_ini_input=None)