# Setup Guide

This guide will help you set up the SQL Generator project for development or production use.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [First-Time Setup](#first-time-setup)
- [Configuration](#configuration)
- [Testing Setup](#testing-setup)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: 2GB RAM minimum (4GB recommended)
- **Storage**: 1GB free space for embeddings
- **OS**: Windows, macOS, or Linux

### Python Dependencies

The project uses modern Python packaging with `pyproject.toml`. All dependencies are automatically handled during installation.

**Core Dependencies:**
- `sentence-transformers>=2.2.2` - For semantic embeddings
- `chromadb>=0.4.0` - Vector database
- `pydantic>=2.0.0` - Data validation
- `numpy>=1.21.0` - Numerical operations

## 🚀 Installation

### Option 1: Standard Installation

```bash
# Clone the repository
git clone https://github.com/shantanupandit/sql-generator.git
cd sql-generator

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the package
pip install -e .
```

### Option 2: Development Installation

```bash
# Clone and enter directory
git clone https://github.com/shantanupandit/sql-generator.git
cd sql-generator

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Option 3: Using Requirements File

```bash
# Install using requirements.txt
pip install -r requirements.txt

# Then install the package
pip install -e .
```

## 🎯 First-Time Setup

### 1. Verify Installation

```bash
# Test basic functionality
python -c "from sql_generator.core import SQLGenerator; print('Installation successful!')"

# Check CLI access
python -m sql_generator.cli --help
```

### 2. Initialize Embeddings

**This step is crucial - the system won't work without embeddings!**

```bash
# Initialize vector embeddings (required for first run)
python -m sql_generator.cli --setup
```

This command will:
- Download the sentence transformer model (~90MB)
- Process your schema file
- Generate vector embeddings for all tables and columns
- Store embeddings in ChromaDB

**Expected output:**
```
✅ Loaded configuration from: data/config/config.json
🤖 SchemaEmbedder initialized: Model: all-MiniLM-L6-v2
📂 VectorStore initialized with persist_dir: data/config/data/chroma_db
📊 Processing schema: data/schemas/tables_schema.json
✅ Successfully created 15 table embeddings
✅ Successfully created 127 column embeddings  
🎉 Setup completed successfully!
```

### 3. Test Basic Functionality

```bash
# Test with a simple query
python -m sql_generator.cli --query "find all customers"

# Test with analysis
python -m sql_generator.cli --analyze --query "show customer orders"
```

### 4. Verify Schema Loading

```bash
# Display loaded schema information
python -m sql_generator.cli --schema-info
```

## ⚙️ Configuration

### Default Configuration

The system uses `data/config/config.json` by default:

```json
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
    "persist_dir": "data/config/data/chroma_db",
    "distance_metric": "cosine"
  }
}
```

### Custom Configuration

Create your own configuration file:

```bash
# Copy default config
cp data/config/config.json my_config.json

# Edit as needed
# Use with CLI
python -m sql_generator.cli --config-path my_config.json --query "test"
```

### Environment Variables

You can also use environment variables:

```bash
# Set custom schema path
export SQL_GENERATOR_SCHEMA_PATH="/path/to/your/schema.json"

# Set custom config
export SQL_GENERATOR_CONFIG_PATH="/path/to/your/config.json"
```

## 🗄️ Schema Setup

### Schema File Format

Create or modify `data/schemas/tables_schema.json`:

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
    },
    "orders": {
      "description": "Customer order information",
      "columns": {
        "order_id": {
          "type": "INTEGER",
          "description": "Unique order identifier",
          "primary_key": true
        },
        "customer_id": {
          "type": "INTEGER", 
          "description": "Reference to customer",
          "foreign_key": {
            "table": "customers",
            "column": "customer_id"
          }
        }
      }
    }
  }
}
```

### Schema Validation

```bash
# Validate your schema format
python -c "
from sql_generator.schema import SchemaLoader
loader = SchemaLoader()
schema = loader.load('data/schemas/tables_schema.json')
print(f'Loaded {len(schema.tables)} tables successfully!')
"
```

## 🧪 Testing Setup

### Basic Test Verification

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sql_generator

# Run specific test category
pytest tests/unit/
```

### Test Dependencies

If you get import errors during testing:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Or use development installation
pip install -e ".[dev]"
```

### Creating Test Data

```bash
# Generate test embeddings (for testing)
python -c "
from sql_generator.schema import SchemaEmbedder
embedder = SchemaEmbedder()
embedder.generate_embeddings('data/schemas/tables_schema.json')
print('Test embeddings generated!')
"
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Collection Not Found Error

**Error:**
```
Collection 'schema_tables' not found
```

**Solution:**
```bash
# Run setup to initialize embeddings
python -m sql_generator.cli --setup
```

#### 2. Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'sql_generator'
```

**Solution:**
```bash
# Install in editable mode
pip install -e .

# Or check Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/sql-generator"
```

#### 3. ChromaDB Initialization Errors

**Error:**
```
Failed to initialize ChromaDB
```

**Solutions:**
```bash
# Clear existing data and reinitialize
rm -rf data/config/data/chroma_db
python -m sql_generator.cli --setup

# Check permissions
ls -la data/config/data/
```

#### 4. Model Download Issues

**Error:**
```
Failed to download sentence transformer model
```

**Solutions:**
```bash
# Manual model download
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model downloaded successfully!')
"

# Use offline mode if needed
export TRANSFORMERS_OFFLINE=1
```

#### 5. Schema Loading Errors

**Error:**
```
Schema file not found or invalid
```

**Solutions:**
```bash
# Check schema file exists
ls -la data/schemas/tables_schema.json

# Validate JSON format
python -m json.tool data/schemas/tables_schema.json

# Use absolute path
python -m sql_generator.cli --schema-path "/absolute/path/to/schema.json"
```

#### 6. Low Memory Issues

**Error:**
```
Out of memory during embedding generation
```

**Solutions:**
```bash
# Reduce batch size in config
{
  "embeddings": {
    "batch_size": 16  // Reduce from 32
  }
}

# Process schema in smaller chunks
# Split large schema files into smaller ones
```

### Diagnostic Commands

```bash
# Check system status
python -c "
from sql_generator.schema import SchemaSearcher
searcher = SchemaSearcher()
stats = searcher.get_stats()
print('System Status:', stats)
"

# Test search functionality
python -c "
from sql_generator.schema import SchemaSearcher
searcher = SchemaSearcher()
results = searcher.search('test', n_results=1)
print(f'Search working: {len(results) >= 0}')
"

# Verify configuration loading
python -c "
from sql_generator.utils import get_config
config = get_config()
print('Config loaded:', config)
"
```

### Getting Help

If you're still having issues:

1. **Check the logs** - Enable verbose mode:
   ```bash
   python -m sql_generator.cli --verbose --query "test"
   ```

2. **Search existing issues** on GitHub

3. **Create a new issue** with:
   - Error message
   - System information (OS, Python version)
   - Steps to reproduce
   - Configuration details

4. **Join discussions** on GitHub for community help

## 🔄 Updating

### Update Installation

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -e . --upgrade

# Regenerate embeddings if schema changed
python -m sql_generator.cli --setup
```

### Migration Between Versions

Check `CHANGELOG.md` for breaking changes and migration instructions.

## ✅ Setup Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -e .`)
- [ ] Embeddings initialized (`--setup`)
- [ ] Basic query test passed
- [ ] Schema information displayed
- [ ] Tests run successfully (if development)

**Congratulations! Your SQL Generator is ready to use! 🎉**

## 📞 Next Steps

- Read the [API Documentation](docs/API.md)
- Explore [Usage Examples](USAGE_GUIDE.md)
- Join the [Community Discussions](https://github.com/shantanupandit/sql-generator/discussions)
