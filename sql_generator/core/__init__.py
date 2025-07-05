"""
Core functionality for the SQL Generator project.
"""

from .generator import SQLGenerator, SQLResult
from .exceptions import (
    SQLGeneratorError,
    SchemaValidationError,
    EmbeddingError,
    ConfigurationError,
    DatabaseConnectionError
)

__all__ = [
    'SQLGenerator',
    'SQLResult',
    'SQLGeneratorError',
    'SchemaValidationError',
    'EmbeddingError',
    'ConfigurationError',
    'DatabaseConnectionError'
]
