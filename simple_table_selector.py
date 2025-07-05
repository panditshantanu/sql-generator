"""
Simple Table Selector - Just the basics for reducing prompt context.
No enterprise components, no complex configurations - just practical table selection.
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict


class SimpleTableSelector:
    """
    Simple table selector that does the minimum needed:
    1. Take semantic search results
    2. Filter out obviously irrelevant tables
    3. Add basic bridge tables if needed
    4. Return a clean list of relevant tables
    """
    
    def __init__(self, bridge_table_rules: Dict[str, List[str]] = None):
        """
        Initialize with optional bridge table rules.
        
        Args:
            bridge_table_rules: Simple mapping like {"cust+prd_mstr": ["ord_hdr", "ord_ln"]}
        """
        self.bridge_rules = bridge_table_rules or {
            # Customer + Product queries need order tables
            "cust+prd_mstr": ["ord_hdr", "ord_ln"],
            "prd_mstr+cust": ["ord_hdr", "ord_ln"],
        }
    
    def select_tables(self, 
                     query: str, 
                     semantic_results: Dict[str, List[Dict]], 
                     max_tables: int = 4) -> List[str]:
        """
        Simple table selection logic.
        
        Args:
            query: User's natural language query
            semantic_results: Results from semantic search
            max_tables: Maximum number of tables to return
            
        Returns:
            List of selected table names
        """
        # Step 1: Extract tables with scores from semantic results
        table_scores = self._extract_table_scores(semantic_results)
        
        # Step 2: Simple filtering - remove very low confidence tables
        filtered_tables = self._filter_low_confidence(table_scores)
        
        # Step 3: Apply basic query-specific filtering
        relevant_tables = self._apply_query_filtering(query, filtered_tables)
        
        # Step 4: Add bridge tables if needed
        final_tables = self._add_bridge_tables(relevant_tables)
        
        # Step 5: Limit to max_tables
        return final_tables[:max_tables]
    
    def _extract_table_scores(self, semantic_results: Dict[str, List[Dict]]) -> Dict[str, float]:
        """Extract table names and their best confidence scores."""
        table_scores = defaultdict(float)
        
        # Get scores from column results
        for col_result in semantic_results.get('columns', []):
            table = col_result.get('table')
            score = col_result.get('score', 0)
            if table and score > table_scores[table]:
                table_scores[table] = score
        
        # Get scores from table results
        for table_result in semantic_results.get('tables', []):
            table = table_result.get('table')
            score = table_result.get('score', 0)
            if table and score > table_scores[table]:
                table_scores[table] = score
        
        return dict(table_scores)
    
    def _filter_low_confidence(self, table_scores: Dict[str, float], 
                              min_score: float = 0.15) -> Dict[str, float]:
        """Remove tables with very low confidence scores."""
        return {
            table: score 
            for table, score in table_scores.items() 
            if score >= min_score
        }
    
    def _apply_query_filtering(self, query: str, table_scores: Dict[str, float]) -> List[str]:
        """Apply simple query-based filtering rules."""
        query_lower = query.lower()
        
        # Get sorted tables by score
        sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Simple exclusion rules
        excluded_tables = set()
        
        # If query is clearly about employees, exclude customer/warehouse tables
        if any(word in query_lower for word in ['employee', 'staff', 'worker']):
            excluded_tables.update(['cust', 'wh_mstr', 'mkt_cmp'])
        
        # If query is clearly about customers, exclude employee/warehouse tables
        elif any(word in query_lower for word in ['customer', 'client', 'buyer']):
            excluded_tables.update(['emp_mstr', 'wh_mstr'])
        
        # If query is clearly about products, include product table highly
        elif any(word in query_lower for word in ['product', 'item', 'inventory']):
            excluded_tables.update(['emp_mstr', 'wh_mstr', 'mkt_cmp'])
        
        # Filter out excluded tables and return top tables
        relevant_tables = [
            table for table, score in sorted_tables 
            if table not in excluded_tables
        ]
        
        return relevant_tables
    
    def _add_bridge_tables(self, relevant_tables: List[str]) -> List[str]:
        """Add bridge tables using simple rules."""
        final_tables = list(relevant_tables)
        
        # Check if we need bridge tables
        table_set = set(relevant_tables)
        
        for rule_key, bridge_tables in self.bridge_rules.items():
            rule_tables = set(rule_key.split('+'))
            
            # If we have the tables mentioned in the rule, add the bridge tables
            if rule_tables.issubset(table_set):
                for bridge_table in bridge_tables:
                    if bridge_table not in final_tables:
                        final_tables.append(bridge_table)
        
        return final_tables


def simple_table_selection_demo(query: str, semantic_results: Dict[str, List[Dict]]):
    """
    Demo function showing simple table selection.
    """
    print(f"\n🎯 Simple Table Selection for: '{query}'")
    print("=" * 60)
    
    # Initialize simple selector
    selector = SimpleTableSelector()
    
    # Select tables
    selected_tables = selector.select_tables(query, semantic_results, max_tables=4)
    
    print(f"📊 Input: {len(semantic_results.get('columns', []))} column matches, {len(semantic_results.get('tables', []))} table matches")
    print(f"✅ Selected Tables: {', '.join(selected_tables)}")
    
    # Show reasoning
    print(f"\n🧠 Simple Logic Applied:")
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['employee', 'staff', 'worker']):
        print(f"   • Detected employee query → excluded customer/warehouse tables")
    elif any(word in query_lower for word in ['customer', 'client', 'buyer']):
        print(f"   • Detected customer query → excluded employee/warehouse tables")
    elif any(word in query_lower for word in ['product', 'item', 'inventory']):
        print(f"   • Detected product query → excluded employee/warehouse/marketing tables")
    
    # Check for bridge tables
    if 'cust' in selected_tables and 'prd_mstr' in selected_tables:
        if 'ord_hdr' in selected_tables or 'ord_ln' in selected_tables:
            print(f"   • Added bridge tables (ord_hdr, ord_ln) to connect customers and products")
    
    print(f"\n💡 Result: Reduced from potentially many tables to {len(selected_tables)} relevant tables")
    
    return selected_tables


# Integration function to replace the complex enterprise logic
def get_relevant_tables_simple(query: str, collection_prefix: str = "schema") -> List[str]:
    """
    Simple function to get relevant tables - replaces all the complex enterprise logic.
    """
    try:
        # Use existing searcher to get semantic results
        from sql_generator.schema.schema_searcher import SchemaSearcher
        
        searcher = SchemaSearcher(verbose=False)
        semantic_results = searcher.search_schema(query, k_columns=10, k_tables=5)
        
        # Use simple selector
        selector = SimpleTableSelector()
        selected_tables = selector.select_tables(query, semantic_results, max_tables=4)
        
        return selected_tables
        
    except Exception as e:
        print(f"❌ Simple table selection failed: {e}")
        return []


if __name__ == "__main__":
    # Test with sample data
    sample_semantic_results = {
        'columns': [
            {'table': 'emp_mstr', 'column': 'fnm', 'score': 0.412},
            {'table': 'emp_mstr', 'column': 'lnm', 'score': 0.382},
            {'table': 'cust', 'column': 'fnm', 'score': 0.340},
            {'table': 'cust', 'column': 'lnm', 'score': 0.328},
            {'table': 'wh_mstr', 'column': 'mgr_nm', 'score': 0.323},
        ],
        'tables': [
            {'table': 'emp_mstr', 'score': 0.286},
            {'table': 'cust', 'score': 0.250},
            {'table': 'wh_mstr', 'score': 0.200},
        ]
    }
    
    # Test employee query
    simple_table_selection_demo("how many employees with name Michael", sample_semantic_results)
    
    # Test customer-product query
    customer_product_results = {
        'columns': [
            {'table': 'prd_mstr', 'column': 'prd_id', 'score': 0.302},
            {'table': 'cust', 'column': 'fnm', 'score': 0.340},
        ],
        'tables': [
            {'table': 'prd_mstr', 'score': 0.280},
            {'table': 'cust', 'score': 0.250},
        ]
    }
    
    simple_table_selection_demo("how many products purchased by Rebecca", customer_product_results)
