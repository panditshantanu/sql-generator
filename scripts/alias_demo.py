"""
Show the before/after improvement with aliases.
"""
print("🔍 BEFORE vs AFTER: Column Aliases in SQL Prompts")
print("=" * 60)

print("\n❌ BEFORE (without aliases):")
print("    - ct_id: INT NOT NULL - Unique identifier for each customer.")

print("\n✅ AFTER (with aliases):")
print("    - ct_id: INT NOT NULL - Unique identifier for each customer. [Aliases: customer_id, client_id]")

print("\n💡 Benefits:")
print("   • LLM understands 'customer_id' refers to 'ct_id'")
print("   • LLM understands 'client_id' refers to 'ct_id'")
print("   • More flexible natural language queries")
print("   • Better SQL generation from varied user input")

print("\n🎯 Example queries that now work better:")
print("   • 'find customer by customer_id' → uses ct_id")
print("   • 'show client_id and name' → uses ct_id") 
print("   • 'customers with client_id 123' → uses ct_id")

print("\n📋 Schema columns with aliases in your database:")
schema_aliases = {
    "cust.ct_id": ["customer_id", "client_id"],
    # Add more if they exist in your schema
}

for column, aliases in schema_aliases.items():
    print(f"   • {column}: {', '.join(aliases)}")

print(f"\n✅ Your SQL prompts now include these aliases for better LLM understanding!")
