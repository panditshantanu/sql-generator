"""
SQL Generator - A natural language to SQL conversion tool.

This package provides tools for converting natural language queries
into SQL statements using semantic search and language models.
"""

from .core import SQLGenerator, SQLResult
from .core.exceptions import (
    SQLGeneratorError,
    SchemaValidationError,
    EmbeddingError,
    ConfigurationError,
    DatabaseConnectionError
)

# CLI import for command-line usage
from .cli import SQLGeneratorCLI

__version__ = "1.0.0"
__author__ = "SQL Generator Team"

__all__ = [
    'SQLGenerator',
    'SQLResult',
    'SQLGeneratorCLI',
    'SQLGeneratorError',
    'SchemaValidationError',
    'EmbeddingError',
    'ConfigurationError',
    'DatabaseConnectionError'
]