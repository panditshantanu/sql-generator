"""Main SQL Generator class providing the primary interface."""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

from .exceptions import SQLGeneratorError, SchemaValidationError
from ..schema.semantic_schema import SemanticSchema
from ..schema.schema_embedder import SchemaEmbedder
from ..schema.vector_store import VectorStore
from ..schema.schema_searcher import SchemaSearcher
from ..llm.sql_prompt_generator import SQLPromptGenerator
from ..utils.config_manager import get_config


class SQLResult:
    """Container for SQL generation results."""
    
    def __init__(self, sql: str, confidence: float = 0.0, metadata: Optional[Dict] = None, prompt: Optional[str] = None):
        """
        Initialize SQL result.
        
        Args:
            sql: Generated SQL query (or prompt for LLM)
            confidence: Confidence score (0.0 to 1.0)
            metadata: Additional metadata about the generation
            prompt: The prompt that was generated for the LLM
        """
        self.sql = sql  # Note: This might contain a prompt instead of SQL
        self.confidence = confidence
        self.metadata = metadata or {}
        self.prompt = prompt
    
    def __str__(self) -> str:
        return self.sql
    
    def __repr__(self) -> str:
        return f"SQLResult(sql='{self.sql[:50]}...', confidence={self.confidence})"


class SQLGenerator:
    """
    Main SQL Generator class that provides a high-level interface
    for generating SQL queries from natural language.
    """
    
    def __init__(self, schema_path: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the SQL Generator.
        
        Args:
            schema_path: Path to the schema JSON file
            config_path: Path to the configuration file
            
        Raises:
            SchemaValidationError: If schema file is invalid or missing
            ConfigurationError: If configuration is invalid
        """
        self.logger = logging.getLogger(__name__)
        self.config = get_config()
        
        # Validate and set schema path
        if schema_path is None:
            schema_path = self.config.get("schema.schema_path")
        
        if not schema_path:
            raise SchemaValidationError("No schema path provided in arguments or configuration")
        
        self.schema_path = Path(schema_path)
        if not self.schema_path.exists():
            raise SchemaValidationError(f"Schema file not found: {schema_path}")
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all required components."""
        try:
            # Load semantic schema
            self.semantic_schema = SemanticSchema(str(self.schema_path))
            
            # Initialize embedder
            self.embedder = SchemaEmbedder()
            
            # Initialize vector store
            self.vector_store = VectorStore()
            
            # Initialize searcher
            self.searcher = SchemaSearcher(self.vector_store)
            
            # Initialize prompt generator
            self.prompt_generator = SQLPromptGenerator()
            
            self.logger.info("SQL Generator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize SQL Generator: {e}")
            raise SQLGeneratorError(f"Initialization failed: {e}")
    
    def generate_sql(self, query: str, **kwargs) -> SQLResult:
        """
        Generate SQL from natural language query.
        
        Args:
            query: Natural language description of the SQL query
            **kwargs: Additional parameters for generation
            
        Returns:
            SQLResult containing the generated SQL and metadata
            
        Raises:
            SQLGeneratorError: If SQL generation fails
        """
        try:
            self.logger.info(f"Generating SQL for query: {query}")
            
            # Search for relevant schema elements
            search_results = self.searcher.search(query)
            
            # Generate prompt for LLM using the prompt generator
            prompt = self.prompt_generator.generate_sql_query(
                user_query=query,
                search_results=search_results,
                **kwargs
            )
            
            # The prompt generator stores the same prompt internally
            stored_prompt = self.prompt_generator.get_last_prompt()
            
            # Calculate confidence based on search results
            confidence = self._calculate_confidence(search_results)
            
            # Create metadata
            metadata = {
                "search_results": search_results,
                "query_length": len(query),
                "tables_used": self._extract_tables_from_results(search_results),
                "original_query": query
            }
            
            # Return the prompt as the "sql" field (for LLM consumption)
            return SQLResult(sql=prompt, confidence=confidence, metadata=metadata, prompt=stored_prompt)
            
        except Exception as e:
            self.logger.error(f"SQL generation failed: {e}")
            raise SQLGeneratorError(f"Failed to generate SQL: {e}")
    
    def _calculate_confidence(self, search_results: List[Dict]) -> float:
        """Calculate confidence score based on search results."""
        if not search_results:
            return 0.0
        
        # Simple confidence calculation based on search scores
        scores = [result.get('score', 0.0) for result in search_results[:5]]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _extract_tables_from_results(self, search_results: List[Dict]) -> List[str]:
        """Extract table names from search results."""
        tables = set()
        for result in search_results:
            # Check top-level 'table' key
            if 'table' in result:
                tables.add(result['table'])
            
            # Check metadata for table information
            metadata = result.get('metadata', {})
            if metadata:
                # Check various possible keys for table name
                table_keys = ['table_name', 'table', 'name']
                for key in table_keys:
                    if key in metadata and metadata[key]:
                        tables.add(metadata[key])
                        break
        
        return list(tables)
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded schema.
        
        Returns:
            Dictionary containing schema information
        """
        try:
            semantic_data = self.semantic_schema.prepare_semantic_data()
            return {
                "tables_count": len(semantic_data.get('tables', [])),
                "columns_count": len(semantic_data.get('columns', [])),
                "schema_path": str(self.schema_path)
            }
        except Exception as e:
            self.logger.error(f"Failed to get schema info: {e}")
            return {"error": str(e)}
    
    def validate_query(self, query: str) -> bool:
        """
        Validate if a natural language query can be processed.
        
        Args:
            query: Natural language query to validate
            
        Returns:
            True if query appears valid, False otherwise
        """
        if not query or not query.strip():
            return False
        
        # Basic validation - check for SQL keywords that might indicate
        # the user is trying to input SQL instead of natural language
        sql_keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY']
        query_upper = query.upper()
        
        # If query contains multiple SQL keywords, it might be SQL, not natural language
        keyword_count = sum(1 for keyword in sql_keywords if keyword in query_upper)
        
        return keyword_count < 3  # Allow some keywords but not too many
    
    def reset_embeddings(self) -> bool:
        """
        Reset and regenerate embeddings from the schema.
        
        Returns:
            True if reset was successful, False otherwise
        """
        try:
            self.logger.info("Resetting embeddings...")
            
            # Clear existing vector store
            self.vector_store.clear()
            
            # Regenerate embeddings
            semantic_data = self.semantic_schema.prepare_semantic_data()
            self.embedder.generate_embeddings(semantic_data)
            
            self.logger.info("Embeddings reset successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset embeddings: {e}")
            return False
