"""
Demonstrate OUTER JOIN queries using the SQL Generator schema.
Shows practical examples that would require LEFT/RIGHT OUTER JOINs.
"""

import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from llm.sql_prompt_generator import SQLPromptGenerator


def demonstrate_outer_join_queries():
    """Show various OUTER JOIN scenarios with the current schema."""
    
    print("🔗 OUTER JOIN Query Examples Based on Your Schema")
    print("=" * 70)
    
    generator = SQLPromptGenerator()
    
    # Define OUTER JOIN scenarios
    outer_join_scenarios = [
        {
            "title": "Products Never Ordered (LEFT OUTER JOIN)",
            "description": "Find all products including those that have never been ordered",
            "query": "show all products including those that have never been ordered",
            "tables": ["prd_mstr", "ord_ln"],
            "expected_sql": """
SELECT p.prd_id, p.prd_nm, p.prc, p.stk_qty,
       CASE WHEN ol.prd_id IS NULL THEN 'Never Ordered' ELSE 'Has Orders' END as order_status
FROM prd_mstr p
LEFT OUTER JOIN ord_ln ol ON p.prd_id = ol.prd_id
WHERE ol.prd_id IS NULL  -- Only products never ordered
ORDER BY p.prd_nm;
            """,
            "explanation": "LEFT OUTER JOIN shows all products, even those without matching orders"
        },
        
        {
            "title": "Customers Without Orders (LEFT OUTER JOIN)", 
            "description": "Find customers who have never placed an order",
            "query": "show all customers including those who have never placed an order",
            "tables": ["cust", "ord_hdr"],
            "expected_sql": """
SELECT c.ct_id, c.fnm, c.lnm, c.eml,
       COUNT(o.ord_id) as total_orders,
       CASE WHEN COUNT(o.ord_id) = 0 THEN 'No Orders' ELSE 'Has Orders' END as status
FROM cust c
LEFT OUTER JOIN ord_hdr o ON c.ct_id = o.ct_id
GROUP BY c.ct_id, c.fnm, c.lnm, c.eml
ORDER BY total_orders ASC, c.lnm;
            """,
            "explanation": "LEFT OUTER JOIN includes all customers, even those without orders"
        },
        
        {
            "title": "Employees Without Manager Info (LEFT OUTER JOIN)",
            "description": "Show all employees including those without manager information",
            "query": "show all employees including those without manager details",
            "tables": ["emp_mstr"],  # Self-join
            "expected_sql": """
SELECT e.emp_id, e.fnm, e.lnm, e.dept_cd, e.rl_cd,
       m.fnm as manager_first_name,
       m.lnm as manager_last_name,
       CASE WHEN m.emp_id IS NULL THEN 'No Manager' ELSE 'Has Manager' END as manager_status
FROM emp_mstr e
LEFT OUTER JOIN emp_mstr m ON e.mgr_id = m.emp_id
ORDER BY e.dept_cd, e.lnm;
            """,
            "explanation": "Self LEFT OUTER JOIN shows all employees, including those without managers (like CEOs)"
        },
        
        {
            "title": "All Products with Order Statistics (LEFT OUTER JOIN)",
            "description": "Show product sales statistics including products with zero sales",
            "query": "show sales statistics for all products including those with zero sales",
            "tables": ["prd_mstr", "ord_ln"],
            "expected_sql": """
SELECT p.prd_id, p.prd_nm, p.cat_cd, p.prc, p.stk_qty,
       COUNT(ol.ln_id) as times_ordered,
       SUM(ol.qty) as total_quantity_sold,
       SUM(ol.ln_ttl) as total_revenue,
       CASE 
           WHEN COUNT(ol.ln_id) = 0 THEN 'Never Sold'
           WHEN COUNT(ol.ln_id) < 5 THEN 'Low Sales'
           ELSE 'Good Sales'
       END as sales_category
FROM prd_mstr p
LEFT OUTER JOIN ord_ln ol ON p.prd_id = ol.prd_id
GROUP BY p.prd_id, p.prd_nm, p.cat_cd, p.prc, p.stk_qty
ORDER BY total_revenue DESC NULLS LAST;
            """,
            "explanation": "LEFT OUTER JOIN ensures all products appear in results, even those never sold"
        },
        
        {
            "title": "Order Headers with Missing Line Items (RIGHT OUTER JOIN)",
            "description": "Find any order headers that might be missing line item details",
            "query": "show orders that might be missing line item details",
            "tables": ["ord_hdr", "ord_ln"],
            "expected_sql": """
SELECT oh.ord_id, oh.ord_dt, oh.ttl_amt, oh.sts_cd,
       COUNT(ol.ln_id) as line_item_count,
       CASE WHEN COUNT(ol.ln_id) = 0 THEN 'Missing Line Items' ELSE 'Has Line Items' END as status
FROM ord_hdr oh
LEFT OUTER JOIN ord_ln ol ON oh.ord_id = ol.ord_id
GROUP BY oh.ord_id, oh.ord_dt, oh.ttl_amt, oh.sts_cd
HAVING COUNT(ol.ln_id) = 0  -- Only orders without line items
ORDER BY oh.ord_dt DESC;
            """,
            "explanation": "LEFT OUTER JOIN reveals orders that exist in header but have no line items"
        }
    ]
    
    # Generate prompts for each scenario
    for i, scenario in enumerate(outer_join_scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['title']}")
        print("-" * 60)
        print(f"Business Need: {scenario['description']}")
        print(f"Tables Involved: {', '.join(scenario['tables'])}")
        print(f"Key Concept: {scenario['explanation']}")
        
        # Generate AI prompt
        print(f"\n🤖 Generated AI Prompt:")
        prompt = generator.generate_advanced_prompt(
            scenario["query"],
            scenario["tables"],
            context=f"OUTER JOIN query for {scenario['title']}"
        )
        
        # Show relevant parts of the prompt
        prompt_lines = prompt.split('\n')
        schema_start = next((i for i, line in enumerate(prompt_lines) if "Database Schema:" in line), 0)
        question_start = next((i for i, line in enumerate(prompt_lines) if "User Question:" in line), len(prompt_lines))
        
        # Show schema section (condensed)
        print("   Schema Context:")
        for line in prompt_lines[schema_start:min(schema_start+8, question_start)]:
            if line.strip():
                print(f"   {line}")
        
        print(f"   Query: {scenario['query']}")
        
        # Show expected SQL pattern
        print(f"\n💡 Expected SQL Pattern:")
        expected_lines = scenario["expected_sql"].strip().split('\n')
        for line in expected_lines[:8]:  # Show first 8 lines
            if line.strip():
                print(f"   {line.strip()}")
        if len(expected_lines) > 8:
            print("   ...")
        
        print()
    
    # Summary of OUTER JOIN use cases
    print("\n🎯 OUTER JOIN Use Cases Summary:")
    print("=" * 50)
    print("✅ LEFT OUTER JOIN - Include ALL records from left table")
    print("   • All products (even never ordered)")
    print("   • All customers (even without orders)")
    print("   • All employees (even without managers)")
    print()
    print("✅ RIGHT OUTER JOIN - Include ALL records from right table")
    print("   • All orders (even with missing details)")
    print()
    print("✅ FULL OUTER JOIN - Include ALL records from both tables")
    print("   • Complete data reconciliation scenarios")
    print()
    print("🔑 Key Benefits:")
    print("   • Identify missing data relationships")
    print("   • Complete business reporting")
    print("   • Data quality analysis")
    print("   • Comprehensive customer/product analysis")


if __name__ == "__main__":
    demonstrate_outer_join_queries()
