#!/usr/bin/env python3
"""
Simple script to create embeddings and test search with correct paths
"""

import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def run_complete_test():
    try:
        from main import create_embeddings_and_store, custom_search_demo
        
        # Step 1: Create embeddings with explicit path
        print("🚀 Step 1: Creating embeddings...")
        schema_path = "../tables_schema.json"  # Correct path from src directory
        
        results = create_embeddings_and_store(
            schema_path=schema_path,
            collection_prefix="schema",
            clear_existing=True
        )
        
        print(f"✅ Embeddings created: {results}")
        
        # Step 2: Test search
        print("\n🔍 Step 2: Testing search...")
        custom_search_demo("how many employees do we have hired before Dec 2023")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_complete_test()
