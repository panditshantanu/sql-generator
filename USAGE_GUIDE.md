# SQL Generator - Usage Guide

## 🚀 Quick Start Commands

**⚠️ FIRST TIME SETUP: You need to initialize embeddings before first use!**

### 0. **First Time Setup** (Required)
```bash
# Option 1: Dedicated setup script
python setup_embeddings.py

# Option 2: Using CLI
python run_sql_generator.py --setup

# Option 3: Using batch command (Windows)
run_commands.bat setup
```
**Why this is needed:** The SQL Generator uses vector embeddings to understand your database schema. This one-time setup creates these embeddings from your schema file.

---

### 1. **Quick Interactive Mode** (Easiest)
```bash
python quick_sql.py
```
- Simple, immediate access
- Shows SQL generation + basic analysis
- Auto-detects if setup is needed
- Perfect for testing queries

### 2. **Full CLI Mode** (Most Features)
```bash
python run_sql_generator.py --interactive
```
- Complete command-line interface
- Advanced analysis options
- Full feature set

### 3. **Windows Batch Commands** (Windows Users)
```cmd
# First-time setup
run_commands.bat setup

# Interactive mode
run_commands.bat

# Quick mode  
run_commands.bat quick

# Show schema info
run_commands.bat schema

# Generate SQL for a query
run_commands.bat query "Show me all customers"

# Generate SQL with detailed analysis
run_commands.bat analyze "Find orders from last month"
```

## 📋 Available Commands

### Setup Commands (Run Once)
```bash
# Initialize embeddings (required first time)
python setup_embeddings.py
python run_sql_generator.py --setup
run_commands.bat setup
```

### Single Query Commands
```bash
# Generate SQL from natural language
python run_sql_generator.py --query "Show me all customers from New York"

# Generate SQL with detailed analysis
python run_sql_generator.py --query "Find customer orders" --analyze

# Show schema information
python run_sql_generator.py --schema-info
```

### Interactive Commands (when in interactive mode)
- **Natural language query**: Just type your query
- **`analyze [query]`**: Generate SQL with detailed analysis
- **`setup`**: Initialize embeddings (if not done already)
- **`schema`**: Show schema information  
- **`help`**: Show available commands
- **`quit`** or **`exit`**: Exit the program

## 💡 Example Queries to Try

### Basic Queries
```
Show me all customers
Find all products
Get employee information
List all orders
```

### Complex Queries
```
Show me customers from New York with their orders
Find the top 10 products by sales
Get employees who have made more than 5 sales
Show customer orders from the last 30 days
Find products that are out of stock
```

### Analysis Commands
```
analyze Show me customer revenue by region
analyze Find the best selling products this month
analyze Get customer retention metrics
```

## 📊 What You'll See

### 1. **Generated SQL**
```sql
SELECT customer_id, customer_name, city 
FROM customers 
WHERE city = 'New York';
```

### 2. **Confidence Score**
- Score from 0.0 to 1.0 indicating confidence in the result

### 3. **Schema Matches** (with analysis)
- Relevant tables and columns found
- Similarity scores for each match
- Collection types (tables vs columns)

### 4. **SQL Structure Analysis** (with analysis)
- Query type (SELECT, INSERT, etc.)
- SQL keywords used
- Complexity indicators (JOINs, subqueries, etc.)

## 🔧 Configuration

### Schema Path
The system looks for your schema file in:
1. Command line argument: `--schema-path path/to/schema.json`
2. Config file setting: `data/config/config.json`
3. Default: `data/schemas/tables_schema.json`

### Verbose Mode
Add `--verbose` for detailed logging:
```bash
python run_sql_generator.py --query "your query" --verbose
```

## 🎯 Tips for Best Results

1. **Use natural language**: "Show me customers" rather than "SELECT * FROM customers"
2. **Be specific**: "customers from New York" is better than "some customers"  
3. **Include context**: "orders from last month" vs just "orders"
4. **Try the analyze mode**: Use `analyze` to understand how the system works

## 🆘 Troubleshooting

### Collection Errors
```
ERROR: Collection [schema_tables] does not exists
ERROR: Collection [schema_columns] does not exists
```
**Solution**: Run the first-time setup:
```bash
python setup_embeddings.py
```

### Schema Not Found
```
❌ Schema file not found: data/schemas/tables_schema.json
```
**Solution**: Check that your schema file exists or specify a different path

### Import Errors
```
❌ Import error: No module named 'sql_generator'
```
**Solution**: Make sure you're running from the project root directory

## 🎯 Complete First-Time Workflow

1. **Setup embeddings** (required once):
   ```bash
   python setup_embeddings.py
   ```

2. **Start using**:
   ```bash
   python quick_sql.py
   ```

3. **Enter your questions**:
   ```
   how many customers with first name Clara
   Show me all orders from last month
   Find products that are out of stock
   ```

4. **Get SQL + Analysis**:
   ```sql
   SELECT COUNT(*) FROM customers WHERE first_name = 'Clara';
   ```

## 📁 Project Structure Reminder
```
sql_generator/           # Main package
├── core/               # Core SQL generation
├── schema/            # Schema processing  
├── llm/               # Language model integration
└── utils/             # Utilities

data/                   # Data files
├── schemas/           # Schema definitions
└── config/           # Configuration

scripts/               # Example scripts
tests/                # Unit tests
```

Enjoy using the SQL Generator! 🎉
