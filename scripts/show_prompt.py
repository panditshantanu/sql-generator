"""
Extract and display the complete generated SQL prompt.
"""
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from main import generate_sql_prompt_data

def show_complete_prompt(query: str):
    """Display the complete generated SQL prompt."""
    
    print(f"🚀 Extracting Complete SQL Prompt for: '{query}'")
    print("=" * 70)
    
    try:
        # Get the tuple
        analysis_data, prompt_string = generate_sql_prompt_data(query)
        
        print(f"✅ Prompt generated successfully!")
        print(f"📊 Analysis Success: {analysis_data['success']}")
        print(f"📏 Prompt Length: {len(prompt_string)} characters")
        print(f"📋 Lines: {len(prompt_string.split(chr(10)))}")
        
        print(f"\n" + "="*70)
        print(f"📋 COMPLETE GENERATED SQL PROMPT:")
        print("="*70)
        print(prompt_string)
        print("="*70)
        
        # Show analysis summary
        print(f"\n📊 ANALYSIS DETAILS:")
        print(f"   Tables Found: {len(analysis_data['relevant_tables'])}")
        print(f"   Relevant Tables: {', '.join(analysis_data['relevant_tables'])}")
        
        if analysis_data['best_matches']['top_column']:
            top_col = analysis_data['best_matches']['top_column']
            print(f"   Best Column: {top_col['table']}.{top_col['column']} ({top_col['confidence']:.1f}%)")
        
        if analysis_data['best_matches']['top_table']:
            top_table = analysis_data['best_matches']['top_table']
            print(f"   Best Table: {top_table['table']} ({top_table['confidence']:.1f}%)")
        
        print(f"\n💡 USAGE:")
        print(f"   1. Copy the prompt above (between the === lines)")
        print(f"   2. Send it to ChatGPT, Claude, or any LLM")
        print(f"   3. Get your SQL query back!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test with the products query
    show_complete_prompt("products never ordered")
