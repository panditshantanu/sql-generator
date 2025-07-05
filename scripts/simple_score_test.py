#!/usr/bin/env python3
"""Simple test to examine raw semantic search scores."""

import sys
from pathlib import Path

# Add paths for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from schema.schema_searcher import SchemaSearcher

def test_raw_scores():
    searcher = SchemaSearcher(verbose=False)
    
    query = "samsung products sold quantities"
    results = searcher.search_tables(query, k=5)
    
    print(f"Query: {query}")
    print("Raw results:")
    
    for i, result in enumerate(results, 1):
        table = result.get('table', 'unknown')
        score = result.get('score', 0)
        print(f"{i}. {table}: {score:.6f}")
    
    scores = [r.get('score', 0) for r in results]
    if scores:
        print(f"\nMin: {min(scores):.6f}")
        print(f"Max: {max(scores):.6f}")
        print(f"Range: {max(scores) - min(scores):.6f}")

if __name__ == "__main__":
    test_raw_scores()
