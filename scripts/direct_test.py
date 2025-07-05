"""
Direct test of SQL prompt generation with alias display.
"""
import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("🔍 DIRECT SQL PROMPT TEST")
print("=" * 50)

try:
    # Import the SQL prompt generator directly
    from llm.sql_prompt_generator import SQLPromptGenerator
    
    print("✅ SQLPromptGenerator imported")
    
    # Initialize with schema
    generator = SQLPromptGenerator()
    print("✅ Generator initialized")
    
    # Generate schema context for customer table
    schema_context = generator.get_schema_context(["cust"])
    schema_text = schema_context["schema_text"]
    
    print(f"✅ Schema context generated ({len(schema_text)} chars)")
    
    # Check for aliases in schema context
    if "Aliases:" in schema_text:
        print("🎯 ALIASES FOUND in schema context!")
        alias_lines = [line for line in schema_text.split('\n') if "Aliases:" in line]
        for line in alias_lines:
            print(f"   📋 {line.strip()}")
    else:
        print("❌ No aliases in schema context")
    
    print(f"\n📊 FULL SCHEMA CONTEXT:")
    print("-" * 30)
    print(schema_text)
    print("-" * 30)
    
    # Generate the full prompt
    print(f"\n🚀 Generating full prompt...")
    full_prompt = generator.auto_generate_prompt(
        "find customer by client id",
        ["cust"],
        "Test query for aliases"
    )
    
    print(f"✅ Full prompt generated ({len(full_prompt)} chars)")
    
    # Check for aliases in full prompt
    if "Aliases:" in full_prompt:
        print("🎯 ALIASES FOUND in full prompt!")
        alias_lines = [line for line in full_prompt.split('\n') if "Aliases:" in line]
        for line in alias_lines:
            print(f"   📋 {line.strip()}")
    else:
        print("❌ No aliases in full prompt")
        
    print(f"\n📋 COMPLETE GENERATED PROMPT:")
    print("=" * 60)
    print(full_prompt)
    print("=" * 60)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
