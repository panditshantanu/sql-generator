#!/usr/bin/env python3
"""Simple debug script to examine the _extract_tables_from_results method."""

import sys
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sql_generator.core.generator import SQLGenerator

# Test the table extraction directly
generator = SQLGenerator()
result = generator.generate_sql('what is the total count of products purchased by customers with first name Mike')

print("Original Query:", result.metadata.get('original_query', 'N/A'))
print("Tables Used (current):", result.metadata.get('tables_used', []))
print("Search Results Count:", len(result.metadata.get('search_results', [])))

# Examine first few search results
search_results = result.metadata.get('search_results', [])
if search_results:
    print("\nFirst 3 search results:")
    for i, sr in enumerate(search_results[:3]):
        print(f"\nResult {i+1}:")
        print(f"  Keys: {list(sr.keys())}")
        if 'metadata' in sr:
            print(f"  Metadata keys: {list(sr['metadata'].keys())}")
            metadata = sr['metadata']
            # Look for table name in different keys
            table_keys = ['table_name', 'table', 'name']
            for key in table_keys:
                if key in metadata:
                    print(f"  Found table via metadata.{key}: {metadata[key]}")
        if 'table' in sr:
            print(f"  Found table via sr.table: {sr['table']}")
