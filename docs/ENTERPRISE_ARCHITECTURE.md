# Enterprise SQL Generator Architecture

## Overview

The SQL Generator has been refactored into an enterprise-grade, domain-agnostic solution with clear separation of concerns and configurable components.

## Architecture Components

### 1. Query Analyzer (`sql_generator/core/query_analyzer.py`)

**Purpose**: Analyzes natural language queries to determine intent and context without hard-coded business logic.

**Key Features**:
- Configurable query patterns via JSON configuration
- Domain-agnostic keyword matching
- Context detection based on configurable rules
- Table suggestion and exclusion logic

**Configuration**: `data/config/query_analysis_config.json`

### 2. Schema Manager (`sql_generator/core/schema_manager.py`)

**Purpose**: Handles table and column selection using semantic search results and query context.

**Key Features**:
- Confidence-based filtering
- Context-aware table selection
- Column distribution across tables
- Relationship inference
- Detailed reasoning and logging

### 3. Main Module (`sql_generator/main.py`)

**Purpose**: Orchestrates the components and provides backward-compatible APIs.

**Key Changes**:
- Removed hard-coded table names and business logic
- Uses enterprise components for analysis
- Maintains backward compatibility for existing integrations

## Configuration System

### Query Analysis Configuration

The system uses JSON configuration files to define:

1. **Table Patterns**: How to identify relevant tables based on keywords
2. **Query Patterns**: How to classify queries and suggest table combinations
3. **Domain Configuration**: Thresholds, limits, and behavior settings

### Example Configuration Structure

```json
{
  "table_patterns": [
    {
      "table_name": "customers",
      "keywords": ["customer", "client", "buyer"],
      "aliases": ["cust", "customer", "c"],
      "relationships": ["orders.customer_id"],
      "exclusion_patterns": ["employee", "staff"]
    }
  ],
  "query_patterns": [
    {
      "pattern_id": "customer_analysis",
      "keywords": ["customer", "client"],
      "required_tables": ["customers"],
      "optional_tables": ["orders"],
      "excluded_tables": ["employees"],
      "confidence_boost": 0.2
    }
  ],
  "domain_config": {
    "min_confidence_threshold": 0.5,
    "max_tables_per_query": 4,
    "enable_context_filtering": true
  }
}
```

## Benefits of New Architecture

### 1. Domain Agnostic
- No hard-coded table names or business logic
- Easily configurable for any domain (retail, healthcare, finance, etc.)
- Template-based configuration system

### 2. Enterprise Grade
- Clear separation of concerns
- Comprehensive logging and reasoning
- Error handling and fallback mechanisms
- Performance optimizations

### 3. Maintainable
- Modular components
- Configuration-driven behavior
- Extensive documentation
- Test-friendly architecture

### 4. Scalable
- Configurable thresholds and limits
- Efficient table/column selection algorithms
- Memory and performance optimizations

## Migration Guide

### For Existing Users

The new architecture maintains backward compatibility. Existing code will continue to work, but you'll get additional benefits:

1. **Better table selection** based on configurable rules
2. **Detailed reasoning** for why tables were selected/excluded
3. **Improved accuracy** through enterprise-grade filtering

### For New Deployments

1. **Copy the template**: Use `query_analysis_config_template.json` as starting point
2. **Customize for your domain**: Define your table patterns and query patterns
3. **Adjust thresholds**: Fine-tune confidence thresholds and limits
4. **Test and iterate**: Run test queries and refine configuration

## Configuration Examples

### E-commerce Domain
```json
{
  "table_patterns": [
    {"table_name": "customers", "keywords": ["customer", "buyer", "client"]},
    {"table_name": "products", "keywords": ["product", "item", "catalog"]},
    {"table_name": "orders", "keywords": ["order", "purchase", "transaction"]}
  ]
}
```

### Healthcare Domain
```json
{
  "table_patterns": [
    {"table_name": "patients", "keywords": ["patient", "person", "individual"]},
    {"table_name": "doctors", "keywords": ["doctor", "physician", "provider"]},
    {"table_name": "appointments", "keywords": ["appointment", "visit", "consultation"]}
  ]
}
```

### Financial Domain
```json
{
  "table_patterns": [
    {"table_name": "accounts", "keywords": ["account", "customer", "client"]},
    {"table_name": "transactions", "keywords": ["transaction", "payment", "transfer"]},
    {"table_name": "loans", "keywords": ["loan", "credit", "mortgage"]}
  ]
}
```

## API Reference

### Query Analyzer

```python
from sql_generator.core.query_analyzer import QueryAnalyzer

# Initialize with custom config
analyzer = QueryAnalyzer("path/to/config.json")

# Analyze query
context = analyzer.analyze_query("Find all customers who purchased products")
print(context.suggested_tables)  # Set of suggested tables
print(context.excluded_tables)   # Set of excluded tables
print(context.query_type)        # Detected query type
```

### Schema Manager

```python
from sql_generator.core.schema_manager import SchemaManager

# Initialize with config
manager = SchemaManager(analyzer, config_dict)

# Select tables
table_result = manager.select_tables(query, semantic_results, available_tables)
print(table_result.selected_tables)    # List of selected tables
print(table_result.selection_reasoning) # Human-readable reasoning

# Select columns
column_result = manager.select_columns(query, semantic_results, selected_tables)
print(column_result.selected_columns)   # List of selected columns
print(column_result.table_distribution) # Columns per table
```

## Best Practices

### 1. Configuration Management
- Version control your configuration files
- Test configuration changes thoroughly
- Use descriptive pattern IDs and comments
- Regularly review and update patterns

### 2. Performance Optimization
- Set appropriate confidence thresholds
- Limit maximum tables and columns per query
- Use strict mode for production environments
- Monitor query performance metrics

### 3. Testing
- Test with diverse query types
- Validate table selection accuracy
- Check edge cases and error conditions
- Verify backward compatibility

### 4. Monitoring
- Log query analysis results
- Track confidence score distributions
- Monitor excluded table patterns
- Analyze selection reasoning

## Troubleshooting

### Common Issues

1. **No tables selected**: Lower confidence threshold in configuration
2. **Too many irrelevant tables**: Add exclusion patterns or increase threshold
3. **Missing expected tables**: Check table patterns and keywords
4. **Performance issues**: Reduce max_tables_per_query or enable strict_mode

### Debug Mode

Enable detailed logging to understand table selection:

```python
import logging
logging.getLogger('sql_generator.core').setLevel(logging.DEBUG)
```

This will show detailed reasoning for table inclusion/exclusion decisions.
