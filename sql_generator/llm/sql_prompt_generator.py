"""
SQL Prompt Generator for creating LLM prompts from database schema.
Handles schema loading, table selection, and SQL query generation prompts.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

try:
    from langchain.prompts import PromptTemplate
except ImportError:
    # Fallback for simple string formatting if langchain is not available
    class PromptTemplate:
        def __init__(self, input_variables: List[str], template: str):
            self.input_variables = input_variables
            self.template = template
        
        def format(self, **kwargs) -> str:
            return self.template.format(**kwargs)

# Import schema components with fallback
try:
    from ..schema.schema_loader import SchemaLoader
except ImportError:
    # Create a minimal fallback if schema_loader is not available
    class SchemaLoader:
        def __init__(self, schema_path: str):
            self.schema_path = schema_path
            self.logger = logging.getLogger(__name__)
            self.logger.warning(f"Using fallback SchemaLoader for {schema_path}")
            self.tables = {}
        
        def get_columns(self, table: str) -> Dict:
            return {}

try:
    from ..utils.config_manager import get_config
except ImportError:
    def get_config():
        return {}


class SQLPromptGenerator:
    """
    Advanced SQL prompt generator with schema integration and LLM support.
    
    Features:
    - Schema-aware prompt generation
    - Table relationship detection
    - Multiple prompt templates for different query types
    - Robust error handling and fallbacks
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the SQL prompt generator.
        
        Args:
            schema_path: Path to schema JSON file (uses config if None)
        """
        self.logger = logging.getLogger(__name__)
        
        # Get schema path from config if not provided
        if schema_path is None:
            config = get_config()
            schema_path = config.get("schema.schema_path")
        
        if not schema_path or not Path(schema_path).exists():
            self.logger.warning(f"Schema file not found: {schema_path}")
            self.loader = None
        else:
            try:
                self.loader = SchemaLoader(schema_path)
                self.logger.info(f"Initialized SQL prompt generator with schema: {schema_path}")
            except Exception as e:
                self.logger.error(f"Failed to load schema: {e}")
                self.loader = None
        
        # Initialize prompt templates
        self._init_templates()
    
    def _init_templates(self):
        """Initialize various prompt templates for different query types."""
        
        # Basic SQL generation template
        self.basic_template = PromptTemplate(
            input_variables=["schema", "question"],
            template="""You are an expert SQL generator. Given the following database schema and a user question, generate a precise SQL query.

Database Schema:
{schema}

User Question: "{question}"

Instructions:
- Generate only the SQL query, no explanations
- Use proper SQL syntax and formatting
- Include appropriate JOINs if multiple tables are needed
- Use aliases for better readability
- Consider NULL values and data types
- Use column aliases when they help clarify the query
- Pay attention to [Aliases: ...] in column definitions for alternative column names
- Pay attention to "Table Aliases: ..." for alternative table names you can reference
- You can use table aliases in your FROM and JOIN clauses for more natural queries

SQL Query:"""
        )
        
        # Advanced template with relationships
        self.advanced_template = PromptTemplate(
            input_variables=["schema", "relationships", "question", "context"],
            template="""You are an expert SQL generator with deep understanding of database relationships.

Database Schema:
{schema}

Table Relationships:
{relationships}

Context: {context}

User Question: "{question}"

Instructions:
- Generate optimized SQL with proper JOINs
- Consider foreign key relationships
- Use appropriate indexes and constraints
- Handle edge cases (NULLs, empty results)
- Optimize for performance
- Use column aliases when they help make queries more readable
- Pay attention to [Aliases: ...] in column definitions for alternative column names
- Pay attention to "Table Aliases: ..." for alternative table names you can reference
- Consider using table aliases (e.g., c for customers, p for products)
- You can use table aliases in your FROM and JOIN clauses for more natural queries

SQL Query:"""
        )
        
        # Analytical queries template
        self.analytics_template = PromptTemplate(
            input_variables=["schema", "question", "aggregation_type"],
            template="""You are an expert SQL analyst. Generate analytical SQL queries for business intelligence.

Database Schema:
{schema}

Query Type: {aggregation_type}
User Question: "{question}"

Instructions:
- Use appropriate aggregate functions (COUNT, SUM, AVG, etc.)
- Include GROUP BY and HAVING clauses when needed
- Consider date/time filtering and formatting
- Use window functions if beneficial
- Format results for business reporting
- Use meaningful column aliases for calculated fields
- Pay attention to [Aliases: ...] in column definitions for alternative column names
- Pay attention to "Table Aliases: ..." for alternative table names you can reference
- Use table aliases for cleaner, more readable queries
- You can use table aliases in your FROM and JOIN clauses for more natural queries

SQL Query:"""
        )
    
    def get_schema_context(self, selected_tables: List[str]) -> Dict[str, Any]:
        """
        Build comprehensive schema context for selected tables.
        
        Args:
            selected_tables: List of table names to include
            
        Returns:
            Dictionary with schema information
        """
        if not self.loader:
            return {"schema_text": "Schema not available", "tables": {}, "relationships": []}
        
        schema_lines = []
        tables_info = {}
        relationships = []
        
        for table in selected_tables:
            try:
                # Get table metadata using the correct method
                table_obj = self.loader.get_table(table)
                if not table_obj:
                    continue
                
                # Build table description with aliases
                schema_lines.append(f"Table: {table}")
                schema_lines.append(f"  Description: {table_obj.description}")
                
                # Add table aliases if available
                if hasattr(table_obj, 'aliases') and table_obj.aliases:
                    aliases_str = ", ".join(table_obj.aliases)
                    schema_lines.append(f"  Table Aliases: {aliases_str}")
                
                # Get columns
                columns = self.loader.get_columns(table)
                tables_info[table] = columns
                
                if columns:
                    schema_lines.append("  Columns:")
                    for col_key, col_meta in columns.items():
                        col_desc = col_meta.description
                        col_type = col_meta.type
                        nullable = col_meta.nullable if col_meta.nullable is not None else True
                        null_str = "NULL" if nullable else "NOT NULL"
                        
                        # Add length/precision info if available
                        type_info = col_type
                        if hasattr(col_meta, 'length') and col_meta.length:
                            type_info += f"({col_meta.length})"
                        elif hasattr(col_meta, 'precision') and col_meta.precision:
                            if isinstance(col_meta.precision, list) and len(col_meta.precision) == 2:
                                type_info += f"({col_meta.precision[0]},{col_meta.precision[1]})"
                        
                        # Build column line with aliases if they exist
                        column_line = f"    - {col_key}: {type_info} {null_str} - {col_desc}"
                        
                        # Add aliases if available
                        if hasattr(col_meta, 'aliases') and col_meta.aliases:
                            aliases_str = ", ".join(col_meta.aliases)
                            column_line += f" [Aliases: {aliases_str}]"
                        
                        schema_lines.append(column_line)
                        
                        # Detect potential foreign keys
                        if col_key.endswith('_id') and col_key != f"{table}_id":
                            potential_ref_table = col_key.replace('_id', '')
                            # Check common variations
                            ref_candidates = [
                                potential_ref_table,
                                f"{potential_ref_table}_mstr",  # For master tables
                                f"{potential_ref_table}_hdr"    # For header tables
                            ]
                            
                            for candidate in ref_candidates:
                                if candidate in selected_tables and candidate != table:
                                    relationships.append(f"{table}.{col_key} → {candidate}.{col_key}")
                                    break
                
                schema_lines.append("")  # spacing between tables
                
            except Exception as e:
                self.logger.error(f"Error processing table {table}: {e}")
                schema_lines.append(f"Table: {table} (Error loading details)")
                schema_lines.append("")
                continue
        
        return {
            "schema_text": "\n".join(schema_lines),
            "tables": tables_info,
            "relationships": relationships
        }
    
    def generate_basic_prompt(self, user_query: str, selected_tables: List[str]) -> str:
        """
        Generate a basic SQL prompt for simple queries.
        
        Args:
            user_query: The user's natural language query
            selected_tables: List of relevant table names
            
        Returns:
            Formatted prompt string
        """
        try:
            schema_context = self.get_schema_context(selected_tables)
            
            return self.basic_template.format(
                schema=schema_context["schema_text"],
                question=user_query
            )
        except Exception as e:
            self.logger.error(f"Error generating basic prompt: {e}")
            return f"Error generating prompt: {e}"
    
    def generate_advanced_prompt(
        self, 
        user_query: str, 
        selected_tables: List[str],
        context: str = ""
    ) -> str:
        """
        Generate an advanced SQL prompt with relationship awareness.
        
        Args:
            user_query: The user's natural language query
            selected_tables: List of relevant table names
            context: Additional context about the query intent
            
        Returns:
            Formatted prompt string
        """
        try:
            schema_context = self.get_schema_context(selected_tables)
            
            relationships_text = "\n".join(schema_context["relationships"])
            if not relationships_text:
                relationships_text = "No explicit relationships detected"
            
            return self.advanced_template.format(
                schema=schema_context["schema_text"],
                relationships=relationships_text,
                question=user_query,
                context=context or "General query"
            )
        except Exception as e:
            self.logger.error(f"Error generating advanced prompt: {e}")
            return f"Error generating prompt: {e}"
    
    def generate_analytics_prompt(
        self,
        user_query: str,
        selected_tables: List[str],
        aggregation_type: str = "general"
    ) -> str:
        """
        Generate a prompt optimized for analytical/aggregation queries.
        
        Args:
            user_query: The user's natural language query
            selected_tables: List of relevant table names
            aggregation_type: Type of aggregation (count, sum, avg, etc.)
            
        Returns:
            Formatted prompt string
        """
        try:
            schema_context = self.get_schema_context(selected_tables)
            
            return self.analytics_template.format(
                schema=schema_context["schema_text"],
                question=user_query,
                aggregation_type=aggregation_type
            )
        except Exception as e:
            self.logger.error(f"Error generating analytics prompt: {e}")
            return f"Error generating prompt: {e}"
    
    def auto_generate_prompt(
        self,
        user_query: str,
        selected_tables: List[str],
        context: str = ""
    ) -> str:
        """
        Automatically choose the best prompt template based on query analysis.
        
        Args:
            user_query: The user's natural language query
            selected_tables: List of relevant table names
            context: Additional context
            
        Returns:
            Formatted prompt string
        """
        query_lower = user_query.lower()
        
        # Detect analytics queries
        analytics_keywords = ['count', 'sum', 'total', 'average', 'avg', 'max', 'min', 
                            'group by', 'having', 'aggregate', 'report', 'statistics']
        if any(keyword in query_lower for keyword in analytics_keywords):
            agg_type = "aggregation"
            if 'count' in query_lower:
                agg_type = "count"
            elif any(word in query_lower for word in ['sum', 'total']):
                agg_type = "sum"
            elif any(word in query_lower for word in ['average', 'avg']):
                agg_type = "average"
            
            return self.generate_analytics_prompt(user_query, selected_tables, agg_type)
        
        # Detect complex queries needing relationships
        complex_keywords = ['join', 'relationship', 'between', 'across', 'multiple']
        if (len(selected_tables) > 1 or 
            any(keyword in query_lower for keyword in complex_keywords)):
            return self.generate_advanced_prompt(user_query, selected_tables, context)
        
        # Default to basic prompt
        return self.generate_basic_prompt(user_query, selected_tables)
    
    def generate_sql_query(
        self, 
        user_query: str, 
        search_results: List[Dict] = None,
        **kwargs
    ) -> str:
        """
        Generate a prompt for LLM to create SQL query from natural language.
        
        Args:
            user_query: Natural language query
            search_results: Schema search results from vector search
            **kwargs: Additional parameters
            
        Returns:
            Generated prompt string (not SQL - this is for LLM consumption)
        """
        try:
            # Extract relevant tables from search results
            selected_tables = []
            if search_results:
                for result in search_results:
                    metadata = result.get('metadata', {})
                    table_name = metadata.get('table_name') or metadata.get('table')
                    if table_name and table_name not in selected_tables:
                        selected_tables.append(table_name)
            
            # If no tables found from search, try to infer from user query
            if not selected_tables and self.loader:
                selected_tables = self._infer_tables_from_query(user_query)
            
            # Generate the prompt for LLM
            if selected_tables:
                prompt = self.auto_generate_prompt(user_query, selected_tables)
                # Store the prompt for access
                self._last_generated_prompt = prompt
                return prompt
            else:
                # Fallback prompt when no tables are identified
                fallback_prompt = f"""You are an expert SQL generator. 

User Question: "{user_query}"

No specific database tables were identified for this query. Please generate a SQL query based on common database patterns and table/column naming conventions that would typically be used for this type of request.

Instructions:
- Make reasonable assumptions about table and column names
- Use standard SQL syntax
- Provide a well-formatted, executable SQL query
- Add comments if assumptions are made

SQL Query:"""
                self._last_generated_prompt = fallback_prompt
                return fallback_prompt
            
        except Exception as e:
            self.logger.error(f"Failed to generate prompt: {e}")
            error_prompt = f"-- Error generating prompt: {e}"
            self._last_generated_prompt = error_prompt
            return error_prompt
    
    def get_last_prompt(self) -> Optional[str]:
        """Get the last generated prompt."""
        return getattr(self, '_last_generated_prompt', None)
    
    def _infer_tables_from_query(self, user_query: str) -> List[str]:
        """Infer table names from user query using simple keyword matching."""
        if not self.loader:
            return []
        
        tables = []
        query_lower = user_query.lower()
        
        # Get all table names from schema
        try:
            if hasattr(self.loader, 'tables'):
                for table_name in self.loader.tables.keys():
                    if table_name.lower() in query_lower:
                        tables.append(table_name)
        except Exception:
            pass
        
        return tables

# Legacy class name for backwards compatibility
class PromptGenerator(SQLPromptGenerator):
    """Legacy class name - use SQLPromptGenerator instead."""
    
    def __init__(self, schema_path: str):
        super().__init__(schema_path)
        self.logger.warning("Using deprecated PromptGenerator class. Use SQLPromptGenerator instead.")
    
    def generate_prompt(self, user_query: str, selected_tables: List[str]) -> str:
        """Legacy method - use generate_basic_prompt instead."""
        return self.generate_basic_prompt(user_query, selected_tables)