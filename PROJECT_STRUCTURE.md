# Project Structure

```
sql-generator/
├── .github/                    # GitHub Actions and templates
│   └── workflows/
│       └── ci.yml             # Continuous Integration
├── .vscode/                   # VS Code configuration (local dev)
├── data/                      # Data files and configuration
│   ├── chroma_db/            # Vector database storage
│   ├── config/               # Configuration files
│   └── schemas/              # Database schema files
├── docs/                     # Documentation
│   └── API.md               # API documentation
├── scripts/                  # Utility scripts
│   ├── README.md            # Scripts documentation
│   └── *.py                 # Various utility scripts
├── sql_generator/           # Main application code
│   ├── __init__.py
│   ├── main.py              # Main entry point
│   ├── cli.py               # Command line interface
│   ├── core/                # Core functionality
│   ├── llm/                 # LLM integration
│   ├── schema/              # Schema management
│   └── utils/               # Utility functions
├── tests/                   # Test suite
│   ├── conftest.py
│   └── unit/
├── .gitignore              # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── CHANGELOG.md            # Version history
├── CONTRIBUTING.md         # Contribution guidelines
├── LICENSE                 # MIT License
├── pyproject.toml          # Python project configuration
├── README.md               # Main project documentation
├── requirements.txt        # Python dependencies
├── run_sql_generator.py    # Alternative entry point
├── SECURITY.md            # Security policy
├── SETUP.md               # Setup instructions
└── USAGE_GUIDE.md         # User guide
```

## Key Directories

- **`sql_generator/`** - Main application code and entry points
- **`tests/`** - Comprehensive test suite
- **`docs/`** - Documentation files
- **`scripts/`** - Development and utility scripts
- **`data/`** - Configuration and schema data
- **`.github/`** - GitHub Actions and repository templates

## Entry Points

- **CLI**: `sqlgen` (installed via pip) or `python -m sql_generator`
- **Direct**: `python run_sql_generator.py`
- **Development**: `python sql_generator/main.py`
