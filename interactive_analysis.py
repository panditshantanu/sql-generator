#!/usr/bin/env python3
"""
Interactive analysis tool - shows only detailed analysis.
"""

import sys
from pathlib import Path

# Add project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def interactive_analysis():
    """Interactive analysis mode."""
    print("🔬 SQL Generator - Analysis Only Mode")
    print("=" * 60)
    print("Enter queries to see detailed analysis.")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)
    
    try:
        from sql_generator.main import generate_sql_prompt_data
        
        while True:
            try:
                query = input("\n💬 Enter your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                print(f"\n🔬 Analyzing: '{query}'")
                print("=" * 80)
                
                # Generate analysis
                prompt, analysis = generate_sql_prompt_data(query, "schema")
                
                if analysis:
                    print(analysis)
                else:
                    print("❌ No analysis data generated")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory.")

if __name__ == "__main__":
    interactive_analysis()
