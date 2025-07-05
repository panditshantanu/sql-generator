#!/usr/bin/env python3
"""
Final working version - Employee search query
"""

import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def search_employees():
    try:
        from schema.schema_searcher import SchemaSearcher
        
        print("🔍 Employee Hiring Query Search")
        print("=" * 60)
        
        # Initialize searcher
        searcher = SchemaSearcher(collection_prefix="schema")
        
        # Your specific query
        query = "how many employees do we have hired before Dec 2023"
        
        print(f"Query: {query}")
        print("-" * 60)
        
        # Search for relevant columns
        print("\n📋 Most Relevant Columns:")
        column_results = searcher.search_columns(query, k=5)
        
        for i, result in enumerate(column_results, 1):
            table = result.get('table', 'unknown')
            column = result.get('column', 'unknown')
            score = result.get('score', 0)
            text = result.get('text', '')
            print(f"  {i}. {table}.{column} (score: {score:.3f})")
            print(f"     Description: {text}")
            print()
        
        # Search for relevant tables
        print("📁 Most Relevant Tables:")
        table_results = searcher.search_tables(query, k=3)
        
        for i, result in enumerate(table_results, 1):
            table = result.get('table', 'unknown')
            score = result.get('score', 0)
            text = result.get('text', '')
            print(f"  {i}. {table} (score: {score:.3f})")
            print(f"     Description: {text}")
            print()
        
        # Show SQL suggestion
        print("💡 Suggested SQL Query Structure:")
        if column_results:
            top_result = column_results[0]
            table_name = top_result.get('table', 'employees')
            date_column = top_result.get('column', 'hire_date')
            
            sql_suggestion = f"""
SELECT COUNT(*) as employee_count
FROM {table_name}
WHERE {date_column} < '2023-12-01';
"""
            print(sql_suggestion)
        
        print("✅ Search completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure embeddings exist: python main.py --mode embed --clean --force")
        print("2. Check collections: python check_collections.py")

if __name__ == "__main__":
    search_employees()
