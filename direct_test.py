#!/usr/bin/env python3
"""
Direct test for relationship completion - minimal version.
"""

print("Starting relationship completion test...")

try:
    import sys
    sys.path.append(".")
    sys.path.append("sql_generator")
    
    print("Importing modules...")
    from sql_generator.core.schema_manager import SchemaManager, RelationshipGraph
    
    print("Creating test data...")
    
    # Simple relationship graph test
    graph = RelationshipGraph(adjacency_list={}, relationship_metadata={})
    
    # Add relationships: cust ↔ ord_hdr ↔ ord_ln ↔ prd_mstr
    graph.add_relationship("cust", "ord_hdr")
    graph.add_relationship("ord_hdr", "ord_ln") 
    graph.add_relationship("ord_ln", "prd_mstr")
    
    print(f"Graph created with {len(graph.adjacency_list)} tables")
    for table, neighbors in graph.adjacency_list.items():
        print(f"  {table} → {list(neighbors)}")
    
    # Test configuration
    config = {
        "table_patterns": [
            {"table_name": "cust", "relationships": ["ord_hdr.ct_id"]},
            {"table_name": "ord_hdr", "relationships": ["cust.ct_id", "ord_ln.ord_id"]},
            {"table_name": "ord_ln", "relationships": ["ord_hdr.ord_id", "prd_mstr.prd_id"]},
            {"table_name": "prd_mstr", "relationships": ["ord_ln.prd_id"]}
        ],
        "enable_relationship_completion": True
    }
    
    print("Creating SchemaManager...")
    schema_manager = SchemaManager(config=config)
    
    print("Testing relationship completion...")
    initial_tables = ["cust", "prd_mstr"]
    completed_tables, bridge_tables = schema_manager._complete_table_relationships(initial_tables)
    
    print(f"Initial: {initial_tables}")
    print(f"Completed: {completed_tables}")
    print(f"Bridges: {bridge_tables}")
    
    # Check if bridge tables were added
    expected_bridges = ["ord_hdr", "ord_ln"]
    success = all(bridge in completed_tables for bridge in expected_bridges)
    
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    
    if success:
        print("✓ Generic relationship completion algorithm working correctly!")
        print("✓ Bridge tables ord_hdr and ord_ln correctly added to connect cust → prd_mstr")
    else:
        print("✗ Algorithm failed to add necessary bridge tables")

except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")
