#!/usr/bin/env python3
"""
Script to run only detailed analysis for a query.
"""

import sys
from pathlib import Path

# Add project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def analyze_query(query: str):
    """Run detailed analysis for a query."""
    print(f"🔬 Detailed Analysis for: '{query}'")
    print("=" * 80)
    
    try:
        from sql_generator.main import generate_sql_prompt_data
        
        # Generate the data (this includes analysis)
        prompt, analysis = generate_sql_prompt_data(query, "schema")
        
        if analysis:
            # Just print the analysis part
            print(analysis)
        else:
            print("❌ No analysis data generated")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Get query from command line arguments
        query = " ".join(sys.argv[1:])
    else:
        # Interactive input
        query = input("💬 Enter your query: ").strip()
    
    if query:
        analyze_query(query)
    else:
        print("❌ No query provided")
