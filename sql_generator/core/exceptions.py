"""Custom exceptions for the SQL Generator project."""


class SQLGeneratorError(Exception):
    """Base exception class for SQL Generator errors."""
    pass


class SchemaValidationError(SQLGeneratorError):
    """Raised when schema validation fails."""
    pass


class EmbeddingError(SQLGeneratorError):
    """Raised when embedding generation fails."""
    pass


class ConfigurationError(SQLGeneratorError):
    """Raised when configuration is invalid."""
    pass


class DatabaseConnectionError(SQLGeneratorError):
    """Raised when database connection fails."""
    pass
