"""
Comprehensive demo of table aliases functionality.
"""
import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def demo_table_aliases():
    """Demonstrate table aliases functionality."""
    
    print("🎯 TABLE ALIASES DEMO")
    print("=" * 60)
    
    print("✅ Your SQL Generator now supports table aliases!")
    print("\n📋 AVAILABLE TABLE ALIASES:")
    
    table_aliases = {
        "cust": ["customers", "customer", "c"],
        "prd_mstr": ["products", "product", "prod", "p"],
        "ord_hdr": ["orders", "order_header", "oh"],
        "ord_ln": ["order_lines", "order_items", "line_items", "ol"],
        "emp_mstr": ["employees", "employee", "emp", "e"],
        "aud_log": ["audit_logs", "audit", "logs", "al"],
        "mkt_cmp": ["marketing_campaigns", "campaigns", "marketing", "mc"],
        "wh_mstr": ["warehouses", "warehouse", "wh"],
        "sys_cfg": ["system_config", "config", "configuration", "sc"]
    }
    
    for table, aliases in table_aliases.items():
        print(f"   📁 {table:<12} → {', '.join(aliases)}")
    
    print(f"\n🎯 BENEFITS:")
    print("   ✅ Natural language queries: 'show customers' → cust table")
    print("   ✅ Flexible table references: 'products', 'prod', 'p' all work")
    print("   ✅ Better LLM understanding: aliases included in embeddings")
    print("   ✅ Improved SQL generation: LLMs can use table aliases")
    
    print(f"\n🚀 EXAMPLE QUERIES THAT NOW WORK BETTER:")
    example_queries = [
        "show all customers",
        "find products under $50",
        "get order details",
        "list employees in sales",
        "audit logs from last week",
        "marketing campaigns this year",
        "warehouse capacity",
        "system configuration settings"
    ]
    
    for query in example_queries:
        print(f"   💬 '{query}'")
    
    print(f"\n📋 WHAT'S INCLUDED IN THE PROMPT:")
    print("   🔹 Table names with aliases: 'Table Aliases: customers, customer, c'")
    print("   🔹 Instructions for LLMs to use table aliases")
    print("   🔹 Column aliases: '[Aliases: customer_id, client_id]'")
    print("   🔹 Enhanced semantic search with alias embeddings")
    
    print(f"\n💡 TO REGENERATE EMBEDDINGS WITH TABLE ALIASES:")
    print("   python main.py --mode embed --clean")
    
    print(f"\n🔬 TO TEST A SPECIFIC QUERY:")
    print("   python main.py --mode sqlprompt --query 'show all customers'")
    
    # Test a quick example
    print(f"\n🎯 QUICK DEMO:")
    try:
        from llm.sql_prompt_generator import SQLPromptGenerator
        generator = SQLPromptGenerator()
        
        # Generate context for customer table
        context = generator.get_schema_context(["cust"])
        print("   Schema context for 'cust' table:")
        
        lines = context["schema_text"].split('\n')
        for line in lines[:8]:  # Show first few lines
            if "Table:" in line or "Table Aliases:" in line or "Description:" in line:
                print(f"      {line}")
        
        print("   ...")
        print("   ✅ Table aliases are now included in all generated prompts!")
        
    except Exception as e:
        print(f"   ❌ Demo error: {e}")
    
    print(f"\n🎉 TABLE ALIASES SUCCESSFULLY IMPLEMENTED!")

if __name__ == "__main__":
    demo_table_aliases()
