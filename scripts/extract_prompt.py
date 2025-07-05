"""
Simple prompt extractor to show exactly where the generated prompt is.
"""
import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("🔍 Loading SQL Generator...")

try:
    from main import generate_sql_prompt_data
    
    print("✅ Loaded successfully!")
    print("🚀 Generating prompt for: 'products never ordered'")
    
    # THIS IS WHERE THE PROMPT IS:
    analysis_data, prompt_string = generate_sql_prompt_data("products never ordered")
    #                ^^^^^^^^^^^^^ THE COMPLETE SQL PROMPT IS HERE!
    
    print(f"\n📊 RESULTS:")
    print(f"   Success: {analysis_data['success']}")
    print(f"   Prompt Length: {len(prompt_string)} characters")
    
    print(f"\n📋 THE COMPLETE PROMPT IS:")
    print("=" * 60)
    print(prompt_string)  # <-- THIS IS YOUR COMPLETE SQL PROMPT!
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Error: {e}")
