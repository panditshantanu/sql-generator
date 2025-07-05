"""Test configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def sample_schema_path():
    """Return path to sample schema file."""
    return Path(__file__).parent.parent / "data" / "schemas" / "tables_schema.json"


@pytest.fixture
def sample_config():
    """Return sample configuration."""
    return {
        "vector_store": {
            "persist_dir": "./test_data/embeddings",
            "verbose": False
        },
        "embeddings": {
            "model_name": "all-MiniLM-L6-v2",
            "enable_caching": False
        },
        "logging": {
            "level": "ERROR"
        }
    }


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sql_generator():
    """Create a SQL generator instance for testing."""
    from sql_generator import SQLGenerator
    schema_path = Path(__file__).parent.parent / "data" / "schemas" / "tables_schema.json"
    return SQLGenerator(schema_path=str(schema_path))
