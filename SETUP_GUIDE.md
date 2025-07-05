# SQL Generator - Environment Setup Guide

## Current Status
✅ **Project files exist and are correct**
❌ **Embeddings need to be generated**

## Quick Setup (3 Steps)

### Step 1: Check Current Status
```bash
python check_environment.py
```

### Step 2: Generate Embeddings (Choose ONE option)

**Option A - Simple (Recommended):**
```bash
python regenerate_embeddings_only.py
```

**Option B - Full Setup:**
```bash
python setup_environment.py
```

### Step 3: Test It Works
```bash
python run_sql_generator.py --interactive
```

## Troubleshooting

### If embeddings fail to generate:
1. Check that `data/schemas/tables_schema.json` exists
2. Make sure you have enough disk space
3. Check that no other Python processes are using the database

### If you get import errors:
1. Make sure you're in the project root directory
2. Check that all required packages are installed:
   ```bash
   pip install -r requirements.txt
   ```

### If the interactive mode doesn't work:
1. Run `python check_environment.py` to see what's missing
2. Regenerate embeddings if needed

## What Each Script Does

- **`check_environment.py`** - Checks what's working and what needs setup
- **`regenerate_embeddings_only.py`** - Just generates embeddings (simple)
- **`setup_environment.py`** - Full setup including cleanup and testing
- **`run_sql_generator.py --interactive`** - The main interactive interface

## Expected Output

After successful setup, you should see:
- ✅ ChromaDB with data
- ✅ Embeddings working (with counts > 0)
- ✅ Enterprise architecture working
- Ability to run interactive mode

## Manual Alternative

If scripts don't work, you can manually run:
```bash
python -c "
from sql_generator.main import create_embeddings_and_store
create_embeddings_and_store(clear_existing=True)
"
```
