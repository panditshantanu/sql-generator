"""
Simple test of the new tuple method.
"""
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from main import generate_sql_prompt_data
    
    print("🧪 Testing tuple method...")
    
    # Test the method
    query = "products never ordered"
    analysis_data, prompt_string = generate_sql_prompt_data(query)
    
    print(f"✅ Method executed successfully!")
    print(f"Query: {analysis_data['query']}")
    print(f"Success: {analysis_data['success']}")
    print(f"Tables found: {len(analysis_data['relevant_tables'])}")
    print(f"Prompt length: {len(prompt_string)} characters")
    
    if analysis_data['best_matches']['top_column']:
        top_col = analysis_data['best_matches']['top_column']
        print(f"Best column: {top_col['table']}.{top_col['column']} ({top_col['confidence']:.1f}%)")
    
    print(f"High confidence columns: {len(analysis_data['column_results']['high_confidence'])}")
    print(f"High confidence tables: {len(analysis_data['table_results']['high_confidence'])}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
