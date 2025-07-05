"""
Quick test to show aliases in the final prompt.
"""
import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("🔍 Quick Alias Test")
print("=" * 40)

try:
    from main import generate_sql_prompt_data
    
    # Generate prompt for a customer query
    analysis_data, prompt_string = generate_sql_prompt_data("find customer by client id")
    
    print(f"✅ Prompt generated: {len(prompt_string)} chars")
    
    # Search for aliases in the prompt
    lines = prompt_string.split('\n')
    alias_lines = [line for line in lines if "Aliases:" in line]
    
    if alias_lines:
        print(f"🎯 Found {len(alias_lines)} lines with aliases:")
        for line in alias_lines:
            print(f"   {line.strip()}")
    else:
        print("❌ No aliases found in prompt")
        
    # Show relevant section of the prompt (around customer table)
    print(f"\n📋 Customer table section of prompt:")
    in_cust = False
    for i, line in enumerate(lines):
        if "Table: cust" in line:
            in_cust = True
            start_line = max(0, i-1)
            # Show next 15 lines
            for j in range(start_line, min(len(lines), i+15)):
                marker = ">>>" if "Aliases:" in lines[j] else "   "
                print(f"{marker} {lines[j]}")
            break
    
    if not in_cust:
        print("❌ Customer table not found in prompt")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
