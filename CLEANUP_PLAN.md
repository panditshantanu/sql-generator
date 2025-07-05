# Directory Structure Cleanup Plan

## CURRENT PROBLEMATIC STRUCTURE:
```
d:\Projects\SqlGenerator\
├── Source/src/          # Original working code (main.py, config.json, etc.)
│   ├── main.py
│   ├── config.json
│   ├── schema/
│   ├── llm/
│   └── chroma_db/
├── src/sql_generator/   # New enterprise structure (mostly empty)
│   └── core/
└── tests/               # New test structure
```

## PROPOSED CLEAN STRUCTURE:
```
d:\Projects\SqlGenerator\
├── sql_generator/                    # Main package (single src)
│   ├── __init__.py
│   ├── config.py                    # Enterprise config
│   ├── main.py                      # CLI interface
│   ├── core/                        # Core business logic
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   └── exceptions.py
│   ├── schema/                      # Schema processing
│   │   ├── __init__.py
│   │   ├── schema_loader.py
│   │   ├── semantic_schema.py
│   │   ├── schema_embedder.py
│   │   ├── vector_store.py
│   │   └── schema_searcher.py
│   ├── llm/                         # LLM integration
│   │   ├── __init__.py
│   │   └── sql_prompt_generator.py
│   ├── api/                         # REST API (new)
│   │   ├── __init__.py
│   │   └── routes.py
│   └── utils/                       # Utilities
│       ├── __init__.py
│       └── config_manager.py
├── tests/                           # Comprehensive tests
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── data/                            # Data files
│   ├── schemas/
│   │   └── tables_schema.json
│   ├── config/
│   │   ├── config.json
│   │   ├── config.dev.json
│   │   └── config.prod.json
│   └── embeddings/                  # Generated embeddings
├── docs/                            # Documentation
├── scripts/                         # Utility scripts
├── pyproject.toml
├── requirements.txt
└── README.md
```

## MIGRATION STEPS:
1. Create new clean structure
2. Move working code from Source/src to sql_generator/
3. Remove duplicate src directories
4. Update all import paths
5. Test everything works
