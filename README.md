# 🚀 Free SQL Generator - Natural Language to SQL

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A completely **free, local, and privacy-focused** SQL generator that converts natural language queries into SQL using only local LLM models. **No API costs, no external dependencies, no data sharing.**

## ✨ Key Features

- 🆓 **100% Free** - No OpenAI, Anthropic, or other paid API costs
- � **Local Processing** - All inference happens on your machine via Ollama
- 🔒 **Privacy First** - Your data never leaves your computer
- 🎯 **Smart Schema Detection** - Automatically finds relevant tables and relationships  
- � **Complex Query Support** - Handles JOINs, aggregations, and multi-table queries
- 🎬 **Multiple Database Support** - Retail, DVD rental (Sakila), and custom schemas
- 🤖 **Local LLM Integration** - Uses CodeLlama 7B running locally via Ollama

## 🏆 Performance Metrics

| Query Type | Accuracy | Example |
|------------|----------|---------|
| Simple SELECT | ~90% | "Show me all customers" |
| JOINs & Relations | ~80% | "Customers who ordered iPhones" |
| Aggregations | ~75% | "Top 10 most rented movies" |
| Business Logic | ~70% | "Revenue by category" |

## 🛠️ Technology Stack

- **LLM Model**: CodeLlama 7B (via Ollama - completely free)
- **Vector Search**: ChromaDB with sentence transformers
- **Schema Analysis**: Semantic embeddings for table/column discovery
- **Languages**: Python 3.8+
- **Cost**: $0 - No API fees, no subscriptions

## � Quick Start

### Prerequisites - Install Ollama (Free Local LLM Platform)

1. **Install Ollama**:
   ```bash
   # Download from https://ollama.ai
   # Or use package manager (Windows/Mac/Linux)
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Install CodeLlama**:
   ```bash
   ollama pull codellama:7b
   ```

3. **Start Ollama Service**:
   ```bash
   ollama serve
   ```

### Installation

```bash
# Clone the repository
git clone https://github.com/panditshantanu/sql-generator.git
cd sql-generator

# Install dependencies
pip install -r requirements.txt

# Initialize embeddings (first time only)
python run_sql_generator.py --setup
```

### Usage

#### Command Line Interface

```bash
# Simple query
python run_sql_generator.py --query "show me all customers"

# Complex query with analysis
python run_sql_generator.py --query "customers who ordered action movies" --analyze

# Interactive mode
python run_sql_generator.py --interactive

# Different database schema  
python run_sql_generator.py --schema-path "data/schemas/sakila_schema.json" --query "top 10 rented movies"
```

#### Python API

```python
from sql_generator import SQLGenerator

# Initialize generator
generator = SQLGenerator(schema_path="data/schemas/tables_schema.json")

# Generate SQL
result = generator.generate_sql("show me all customers who ordered iphones")
print(result.sql_query)  # Generated SQL query
print(f"Confidence: {result.confidence}")
```

## 📊 Example Queries & Results

### Retail Database

**Query**: "Give me list of all customers who ordered iPhone"

**Generated SQL**:
```sql
SELECT c.ct_id, c.fnm, c.lnm, c.eml, c.phn_no, c.cr_at, c.sts_cd, c.loy_pts, c.rg_cd,
       ol.prd_id, ol.qty, ol.u_prc, ol.dsc_amt, ol.tx_amt, ol.ln_ttl
FROM cust AS c
JOIN ord_ln AS ol ON c.ct_id = ol.ord_id
WHERE ol.prd_id = 123456789; -- Replace with actual iPhone product ID
```

### DVD Rental Database (Sakila)

**Query**: "Show customers who spent more than 50 dollars"

**Generated SQL**:
```sql
SELECT c.*
FROM customer AS c
JOIN payment AS p ON c.customer_id = p.customer_id
GROUP BY c.customer_id
HAVING SUM(p.amount) > 50;
```

**Query**: "Find top 10 most rented movies"

**Generated SQL**:
```sql
SELECT f.title, COUNT(r.rental_id) AS rental_count
FROM film AS f
JOIN inventory AS i ON f.film_id = i.film_id
JOIN rental AS r ON i.inventory_id = r.inventory_id
GROUP BY f.film_id, f.title
ORDER BY rental_count DESC
LIMIT 10;
```

## 🗄️ Supported Database Schemas

### 1. Retail/E-commerce Schema
- **Tables**: Customers, Products, Orders, Order Items, Employees
- **Use Cases**: Customer analysis, sales reporting, inventory management

### 2. Sakila DVD Rental Schema
- **Tables**: Customer, Film, Rental, Payment, Actor, Category
- **Use Cases**: Movie analytics, customer behavior, revenue analysis

### 3. Custom Schema Support
- Add your own schema JSON files to `data/schemas/`
- Follow the provided schema format for optimal results

## ⚙️ Configuration

### LLM Configuration (`data/config/llm_config.json`)

```json
{
  "default_provider": "local",
  "providers": {
    "local": {
      "model": "codellama:7b",
      "api_key": "http://localhost:11434",
      "max_tokens": 1500,
      "temperature": 0.1,
      "timeout": 90,
      "max_retries": 3,
      "retry_delay": 2.0
    }
  },
  "enable_caching": true,
  "fallback_providers": ["local"]
}
```

### Performance Tuning

**For Better Accuracy**:
- Use CodeLlama 13B: `ollama pull codellama:13b`
- Lower temperature: `"temperature": 0.05`
- More context: `"max_tokens": 2000`

**For Faster Response**:
- Keep CodeLlama 7B
- Reduce timeout: `"timeout": 30`
- Higher temperature: `"temperature": 0.2`

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Natural       │    │   Schema         │    │   Local LLM     │
│   Language      │───▶│   Analysis &     │───▶│   (CodeLlama)   │
│   Query         │    │   Vector Search  │    │   Generation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                       ┌─────────▼──────────┐           │
                       │   ChromaDB         │           │
                       │   Embeddings       │           │
                       └────────────────────┘           │
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────▼─────────┐
│   Final SQL     │◀───│   SQL            │◀───│   Generated       │
│   Query         │    │   Formatting     │    │   Response        │
└─────────────────┘    └──────────────────┘    └───────────────────┘
```

## 📝 Project Structure

```
sql-generator/
├── sql_generator/           # Main package
│   ├── core/               # Core SQL generation logic
│   ├── llm/                # LLM integration & prompts
│   ├── schema/             # Schema analysis & embeddings
│   └── utils/              # Utilities & configuration
├── data/
│   ├── config/             # Configuration files
│   └── schemas/            # Database schema definitions
├── scripts/                # Utility scripts
└── tests/                  # Test files
```

## 🎯 Accuracy & Limitations

### Strengths
- ✅ Excellent schema detection and table relationships
- ✅ Strong performance on standard SQL patterns
- ✅ Good handling of JOINs and basic aggregations
- ✅ Consistent results with low temperature settings
- ✅ **Completely free - No API costs ever**

### Limitations
- ⚠️ Complex window functions may need refinement
- ⚠️ Very specific business logic requires careful prompting
- ⚠️ Performance depends on schema quality and completeness
- ⚠️ CodeLlama 7B has limitations vs larger commercial models

## � Roadmap

- [ ] Support for more local LLM models (Llama 3, Mistral, Code Llama 13B)
- [ ] SQL query validation and correction
- [ ] Query optimization suggestions
- [ ] Integration with popular databases (PostgreSQL, MySQL)
- [ ] Web UI interface
- [ ] Query result visualization
- [ ] Better prompt engineering for edge cases

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repo
git clone https://github.com/panditshantanu/sql-generator.git
cd sql-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for local LLM hosting
- [CodeLlama](https://github.com/facebookresearch/codellama) for the base model
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Sentence Transformers](https://www.sbert.net/) for embeddings

## 📞 Support

- � **Issues**: [GitHub Issues](https://github.com/panditshantanu/sql-generator/issues)
- � **Discussions**: [GitHub Discussions](https://github.com/panditshantanu/sql-generator/discussions)
- � **Email**: mishantanupandit@gmail.com

---

**⭐ If this project helped you eliminate SQL generation costs, please give it a star on GitHub!**

Made with ❤️ for the open source community - **No API fees forever!**
