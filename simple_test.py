#!/usr/bin/env python3
"""
Simple test for the generic relationship completion algorithm.
"""

import sys
import json
from pathlib import Path

# Simple config for testing
test_config = {
    "table_patterns": [
        {
            "table_name": "cust",
            "keywords": ["customer"],
            "relationships": ["ord_hdr.ct_id"],
            "exclusion_patterns": []
        },
        {
            "table_name": "ord_hdr",
            "keywords": ["order"],
            "relationships": ["cust.ct_id", "ord_ln.ord_id"],
            "exclusion_patterns": []
        },
        {
            "table_name": "ord_ln",
            "keywords": ["line"],
            "relationships": ["ord_hdr.ord_id", "prd_mstr.prd_id"],
            "exclusion_patterns": []
        },
        {
            "table_name": "prd_mstr",
            "keywords": ["product"],
            "relationships": ["ord_ln.prd_id"],
            "exclusion_patterns": []
        }
    ],
    "domain_config": {
        "min_confidence_threshold": 0.5,
        "enable_relationship_completion": True
    }
}

def test_basic_functionality():
    """Test basic functionality of SchemaManager."""
    print("Testing basic SchemaManager functionality...")
    
    # Import here to avoid path issues
    sys.path.append("d:/Projects/SqlGenerator")
    from sql_generator.core.schema_manager import SchemaManager
    
    # Create schema manager with test config
    schema_manager = SchemaManager(config=test_config)
    
    # Test relationship graph building
    print(f"Relationship graph has {len(schema_manager.relationship_graph.adjacency_list)} tables")
    
    for table, neighbors in schema_manager.relationship_graph.adjacency_list.items():
        print(f"  {table} → {list(neighbors)}")
    
    # Test path finding
    paths = schema_manager._find_relationship_paths("cust", "prd_mstr")
    print(f"\nPaths from cust to prd_mstr: {paths}")
    
    # Test relationship completion
    initial_tables = ["cust", "prd_mstr"]
    completed_tables, bridge_tables = schema_manager._complete_table_relationships(initial_tables)
    
    print(f"\nInitial tables: {initial_tables}")
    print(f"Completed tables: {completed_tables}")
    print(f"Bridge tables added: {bridge_tables}")
    
    # Validate results
    expected_bridge_tables = ["ord_hdr", "ord_ln"]
    success = all(bridge in completed_tables for bridge in expected_bridge_tables)
    
    if success:
        print("✓ SUCCESS: Bridge tables correctly added!")
    else:
        print("✗ FAILURE: Missing bridge tables")
        
    return success

if __name__ == "__main__":
    try:
        success = test_basic_functionality()
        print(f"\nTest {'PASSED' if success else 'FAILED'}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
