# API Documentation

## Overview

The SQL Generator provides both a command-line interface and a Python API for generating SQL prompts from natural language queries using semantic search.

## Core Classes

### SQLGenerator

Main orchestration class that coordinates schema loading, semantic search, and prompt generation.

```python
from sql_generator.core import SQLGenerator

# Initialize with schema
generator = SQLGenerator(schema_path="path/to/schema.json")

# Generate SQL prompt
result = generator.generate_sql("find all customers")
```

#### Methods

##### `__init__(schema_path: str, config_path: Optional[str] = None)`

Initialize the SQL generator.

**Parameters:**
- `schema_path` (str): Path to JSON schema file
- `config_path` (Optional[str]): Path to configuration file

**Example:**
```python
generator = SQLGenerator(
    schema_path="data/schemas/tables_schema.json",
    config_path="data/config/config.json"
)
```

##### `generate_sql(query: str) -> SQLResult`

Generate SQL prompt from natural language query.

**Parameters:**
- `query` (str): Natural language query

**Returns:**
- `SQLResult`: Object containing generated prompt and metadata

**Example:**
```python
result = generator.generate_sql("show me customers from New York")
print(result.sql)        # Generated prompt
print(result.confidence) # Overall confidence score
print(result.tables)     # Selected tables
```

### SchemaSearcher

Handles semantic search operations on schema embeddings.

```python
from sql_generator.schema import SchemaSearcher

searcher = SchemaSearcher(verbose=True)
results = searcher.search("customer information", n_results=5)
```

#### Methods

##### `search(query: str, n_results: int = 10, collection_types: List[str] = None) -> List[Dict]`

Search for relevant schema elements.

**Parameters:**
- `query` (str): Search query
- `n_results` (int): Maximum results to return
- `collection_types` (List[str]): Types to search ['schema_tables', 'schema_columns']

**Returns:**
- `List[Dict]`: Search results with scores and metadata

**Example:**
```python
results = searcher.search(
    query="customer orders",
    n_results=10,
    collection_types=['schema_tables']
)

for result in results:
    print(f"Table: {result['content']}")
    print(f"Score: {result['score']:.3f}")
    print(f"Metadata: {result['metadata']}")
```

##### `search_tables(query: str, n_results: int = 5) -> List[Dict]`

Search specifically for table-related results.

##### `search_columns(query: str, n_results: int = 10) -> List[Dict]`

Search specifically for column-related results.

##### `get_stats() -> Dict`

Get statistics about the search index.

**Returns:**
- `Dict`: Index statistics including collection counts

### VectorStore

Manages ChromaDB storage for schema embeddings.

```python
from sql_generator.schema import VectorStore

store = VectorStore(persist_dir="data/chroma_db")
```

#### Methods

##### `create_collection(name: str, reset: bool = False) -> Collection`

Create or load a ChromaDB collection.

**Parameters:**
- `name` (str): Collection name
- `reset` (bool): Whether to reset existing collection

##### `store_embeddings(collection_name: str, embeddings: List, documents: List, metadatas: List)`

Store embeddings in collection.

### SchemaEmbedder

Generates vector embeddings for schema elements.

```python
from sql_generator.schema import SchemaEmbedder

embedder = SchemaEmbedder(model_name="all-MiniLM-L6-v2")
embedding = embedder.embed_text("customer table")
```

## Data Structures

### SQLResult

Result object returned by `generate_sql()`.

```python
@dataclass
class SQLResult:
    sql: str                    # Generated SQL prompt
    confidence: float           # Overall confidence (0-100)
    tables: List[str]          # Selected table names
    columns: List[Dict]        # Selected columns with metadata
    analysis: Dict             # Detailed analysis data
    prompt: Optional[str] = None  # Raw prompt (same as sql)
```

### Search Result

Structure returned by search operations.

```python
{
    'content': str,           # Schema element content
    'score': float,           # Similarity score (0-1)
    'distance': float,        # Vector distance
    'metadata': dict,         # Element metadata
    'collection_type': str,   # 'schema_tables' or 'schema_columns'
    'rank': int              # Result ranking
}
```

## Configuration

### Config Structure

```python
{
    "embeddings": {
        "model_name": "all-MiniLM-L6-v2",
        "batch_size": 32,
        "cache_embeddings": true
    },
    "schema": {
        "schema_path": "data/schemas/tables_schema.json"
    },
    "search": {
        "min_confidence": 30.0,
        "max_results": 10,
        "table_limit": 5,
        "column_limit": 20
    },
    "vector_store": {
        "persist_dir": "data/chroma_db",
        "distance_metric": "cosine"
    }
}
```

### Loading Configuration

```python
from sql_generator.utils import get_config

config = get_config("path/to/config.json")
model_name = config.get("embeddings.model_name", "all-MiniLM-L6-v2")
```

## Schema Format

### JSON Schema Structure

```json
{
  "tables": {
    "table_name": {
      "description": "Table description",
      "columns": {
        "column_name": {
          "type": "DATA_TYPE",
          "description": "Column description",
          "nullable": true/false,
          "primary_key": true/false,
          "foreign_key": {
            "table": "referenced_table",
            "column": "referenced_column"
          }
        }
      },
      "relationships": [
        {
          "type": "one_to_many",
          "table": "related_table",
          "on": "join_condition"
        }
      ]
    }
  }
}
```

### Example Schema

```json
{
  "tables": {
    "customers": {
      "description": "Customer information and contact details",
      "columns": {
        "customer_id": {
          "type": "INTEGER",
          "description": "Unique customer identifier",
          "primary_key": true,
          "nullable": false
        },
        "first_name": {
          "type": "VARCHAR(50)",
          "description": "Customer first name",
          "nullable": false
        },
        "email": {
          "type": "VARCHAR(100)",
          "description": "Customer email address",
          "nullable": true
        }
      }
    }
  }
}
```

## Error Handling

### Custom Exceptions

```python
from sql_generator.core.exceptions import (
    SQLGeneratorError,
    SchemaLoadError,
    EmbeddingError,
    SearchError
)

try:
    result = generator.generate_sql("invalid query")
except SchemaLoadError as e:
    print(f"Schema loading failed: {e}")
except SearchError as e:
    print(f"Search failed: {e}")
except SQLGeneratorError as e:
    print(f"General error: {e}")
```

### Common Error Scenarios

1. **Schema File Not Found**
```python
# Handle missing schema file
try:
    generator = SQLGenerator("nonexistent.json")
except SchemaLoadError:
    print("Schema file not found")
```

2. **Collection Not Initialized**
```python
# Check if embeddings are initialized
try:
    results = searcher.search("query")
except SearchError:
    print("Run --setup to initialize embeddings")
```

3. **Low Confidence Results**
```python
# Handle low confidence
result = generator.generate_sql("vague query")
if result.confidence < 50:
    print("Low confidence result, consider refining query")
```

## Performance Optimization

### Embedding Caching

```python
# Enable embedding caching
searcher = SchemaSearcher()
searcher.clear_cache()  # Clear when needed
```

### Batch Processing

```python
# Process multiple queries efficiently
queries = ["query1", "query2", "query3"]
results = []

for query in queries:
    result = generator.generate_sql(query)
    results.append(result)
```

### Vector Store Optimization

```python
# Optimize ChromaDB settings
store = VectorStore(
    persist_dir="data/chroma_db",
    # ChromaDB will auto-tune for your data size
)
```

## Advanced Usage

### Custom Scoring

```python
# Implement custom confidence scoring
def custom_normalize_score(score):
    if score >= 0.8:
        return min(100.0, 90 + (score - 0.8) * 50)
    elif score >= 0.6:
        return 70 + (score - 0.6) * 100
    else:
        return score * 116.67  # Linear scaling for low scores

# Apply in filter_and_rank_results function
```

### Multi-Schema Support

```python
# Load multiple schemas
schemas = ["retail.json", "warehouse.json", "analytics.json"]

for schema_path in schemas:
    generator = SQLGenerator(schema_path=schema_path)
    # Process each schema separately
```

### Custom Collection Types

```python
# Search specific collection types
results = searcher.search(
    query="customer data",
    collection_types=["schema_tables"],  # Tables only
    n_results=5
)
```

## Testing

### Unit Testing

```python
import pytest
from sql_generator.core import SQLGenerator

def test_sql_generation():
    generator = SQLGenerator("test_schema.json")
    result = generator.generate_sql("find customers")
    
    assert result.sql is not None
    assert result.confidence > 0
    assert len(result.tables) > 0

def test_schema_search():
    from sql_generator.schema import SchemaSearcher
    
    searcher = SchemaSearcher()
    results = searcher.search("test query")
    
    assert isinstance(results, list)
    for result in results:
        assert 'score' in result
        assert 'content' in result
```

### Integration Testing

```python
def test_end_to_end():
    # Test complete workflow
    generator = SQLGenerator("data/schemas/test_schema.json")
    
    # Test various query types
    queries = [
        "find all customers",
        "show orders from last month", 
        "customer information with addresses"
    ]
    
    for query in queries:
        result = generator.generate_sql(query)
        assert result.sql is not None
        assert result.confidence > 20  # Minimum acceptable confidence
```

## Migration Guide

### From Version 0.x to 1.x

1. **Updated Configuration Format**
```python
# Old format (deprecated)
config = {
    "model": "all-MiniLM-L6-v2",
    "threshold": 0.3
}

# New format
config = {
    "embeddings": {
        "model_name": "all-MiniLM-L6-v2"
    },
    "search": {
        "min_confidence": 30.0
    }
}
```

2. **New Schema Format**
```json
// Old schema (still supported)
{
  "customers": {
    "customer_id": "INTEGER",
    "name": "VARCHAR(100)"
  }
}

// New schema (recommended)
{
  "tables": {
    "customers": {
      "description": "Customer data",
      "columns": {
        "customer_id": {
          "type": "INTEGER",
          "description": "Unique ID"
        }
      }
    }
  }
}
```

3. **Updated CLI Commands**
```bash
# Old command
python sql_generator.py --query "find customers"

# New command  
python -m sql_generator.cli --query "find customers"
```
