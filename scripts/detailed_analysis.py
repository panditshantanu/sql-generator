"""
Enhanced detailed analysis script for SQL prompt generation.
Shows complete analysis without truncation.
"""
import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def detailed_sql_analysis(query: str):
    """
    Generate detailed SQL analysis with complete information.
    
    Args:
        query: The natural language query to analyze
    """
    print(f"🔍 DETAILED SQL ANALYSIS")
    print("=" * 80)
    print(f"📝 Query: '{query}'")
    print("=" * 80)
    
    try:
        from main import generate_sql_prompt_data
        
        # Generate the analysis
        analysis_data, prompt_string = generate_sql_prompt_data(query)
        
        # SECTION 1: OVERVIEW
        print(f"\n📊 OVERVIEW")
        print("-" * 40)
        print(f"✅ Success: {analysis_data['success']}")
        print(f"📏 Prompt Length: {len(prompt_string)} characters")
        print(f"📋 Prompt Lines: {len(prompt_string.split(chr(10)))}")
        print(f"🎯 Tables Found: {len(analysis_data['relevant_tables'])}")
        print(f"📊 Relevant Tables: {', '.join(analysis_data['relevant_tables'])}")
        
        # SECTION 2: SUMMARY STATISTICS
        summary = analysis_data['summary']
        print(f"\n📈 SEARCH STATISTICS")
        print("-" * 40)
        print(f"📋 Total Column Matches: {summary['total_column_matches']}")
        print(f"   🎯 High Confidence: {summary['high_confidence_columns']}")
        print(f"📁 Total Table Matches: {summary['total_table_matches']}")
        print(f"   🎯 High Confidence: {summary['high_confidence_tables']}")
        
        # SECTION 3: BEST MATCHES
        best = analysis_data['best_matches']
        print(f"\n🏆 BEST MATCHES")
        print("-" * 40)
        if best['top_column']:
            col = best['top_column']
            print(f"🥇 Best Column: {col['table']}.{col['column']}")
            print(f"   📊 Confidence: {col['confidence']:.1f}%")
            print(f"   📝 Text: {col.get('text', 'N/A')[:100]}...")
        else:
            print("🥇 Best Column: None found")
            
        if best['top_table']:
            tbl = best['top_table']
            print(f"🏆 Best Table: {tbl['table']}")
            print(f"   📊 Confidence: {tbl['confidence']:.1f}%")
            print(f"   📝 Text: {tbl.get('text', 'N/A')[:100]}...")
        else:
            print("🏆 Best Table: None found")
        
        # SECTION 4: DETAILED COLUMN ANALYSIS
        col_results = analysis_data['column_results']
        print(f"\n📋 DETAILED COLUMN ANALYSIS")
        print("-" * 40)
        
        # High confidence columns
        if col_results['high_confidence']:
            print(f"🎯 HIGH CONFIDENCE COLUMNS ({len(col_results['high_confidence'])}):")
            for i, col in enumerate(col_results['high_confidence'], 1):
                print(f"  {i}. {col['table']}.{col['column']} ({col['confidence']:.1f}%)")
                print(f"     📝 {col.get('text', 'N/A')[:120]}...")
                print()
        
        # Medium confidence columns
        if col_results['medium_confidence']:
            print(f"🔍 MEDIUM CONFIDENCE COLUMNS ({len(col_results['medium_confidence'])}):")
            for i, col in enumerate(col_results['medium_confidence'], 1):
                print(f"  {i}. {col['table']}.{col['column']} ({col['confidence']:.1f}%)")
                print(f"     📝 {col.get('text', 'N/A')[:120]}...")
                print()
        
        # Low confidence columns (show first 3)
        if col_results['low_confidence']:
            print(f"⚠️  LOW CONFIDENCE COLUMNS ({len(col_results['low_confidence'])}, showing first 3):")
            for i, col in enumerate(col_results['low_confidence'][:3], 1):
                print(f"  {i}. {col['table']}.{col['column']} ({col['confidence']:.1f}%)")
                print(f"     📝 {col.get('text', 'N/A')[:120]}...")
                print()
        
        # SECTION 5: DETAILED TABLE ANALYSIS
        tbl_results = analysis_data['table_results']
        print(f"\n📁 DETAILED TABLE ANALYSIS")
        print("-" * 40)
        
        # High confidence tables
        if tbl_results['high_confidence']:
            print(f"🎯 HIGH CONFIDENCE TABLES ({len(tbl_results['high_confidence'])}):")
            for i, tbl in enumerate(tbl_results['high_confidence'], 1):
                print(f"  {i}. {tbl['table']} ({tbl['confidence']:.1f}%)")
                print(f"     📝 {tbl.get('text', 'N/A')[:120]}...")
                print()
        
        # Medium confidence tables
        if tbl_results['medium_confidence']:
            print(f"🔍 MEDIUM CONFIDENCE TABLES ({len(tbl_results['medium_confidence'])}):")
            for i, tbl in enumerate(tbl_results['medium_confidence'], 1):
                print(f"  {i}. {tbl['table']} ({tbl['confidence']:.1f}%)")
                print(f"     📝 {tbl.get('text', 'N/A')[:120]}...")
                print()
        
        # SECTION 6: RECOMMENDED SQL APPROACH
        print(f"\n💡 RECOMMENDED SQL APPROACH")
        print("-" * 40)
        relevant_tables = analysis_data['relevant_tables']
        
        if len(relevant_tables) == 1:
            print(f"🎯 Single Table Query:")
            print(f"   • Focus on: {relevant_tables[0]}")
        elif len(relevant_tables) > 1:
            print(f"🔗 Multi-Table Query (JOINs needed):")
            for table in relevant_tables:
                print(f"   • {table}")
            
            # Suggest JOIN strategy based on common patterns
            if 'cust' in relevant_tables and any('ord' in t for t in relevant_tables):
                print(f"   💡 Likely JOIN: customers ↔ orders (ct_id)")
            if 'prd_mstr' in relevant_tables and 'ord_ln' in relevant_tables:
                print(f"   💡 Likely JOIN: products ↔ order_lines (prd_id)")
            if 'ord_hdr' in relevant_tables and 'ord_ln' in relevant_tables:
                print(f"   💡 Likely JOIN: order_header ↔ order_lines (ord_id)")
        
        # SECTION 7: COMPLETE GENERATED PROMPT
        print(f"\n📋 COMPLETE GENERATED PROMPT")
        print("=" * 80)
        print(prompt_string)
        print("=" * 80)
        
        # SECTION 8: PROGRAMMATIC ACCESS GUIDE
        print(f"\n💻 PROGRAMMATIC ACCESS")
        print("-" * 40)
        print(f"# To get this data programmatically:")
        print(f"from main import generate_sql_prompt_data")
        print(f"analysis, prompt = generate_sql_prompt_data('{query}')")
        print(f"")
        print(f"# Access specific data:")
        print(f"tables = analysis['relevant_tables']  # {analysis_data['relevant_tables']}")
        print(f"top_col = analysis['best_matches']['top_column']  # {best['top_column']['table'] if best['top_column'] else 'None'}.{best['top_column']['column'] if best['top_column'] else 'None'}")
        print(f"confidence = analysis['best_matches']['top_column']['confidence']  # {best['top_column']['confidence']:.1f}% confidence" if best['top_column'] else "# No top column")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "list all the buyers who have purchased LG products"
    
    detailed_sql_analysis(query)
