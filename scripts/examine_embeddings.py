#!/usr/bin/env python3
"""Examine the embedded text for tables to understand scoring issues."""

import sys
from pathlib import Path

# Add paths for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from schema.vector_store import VectorStore

def examine_table_embeddings():
    """Look at what text is stored for each table."""
    
    vector_store = VectorStore(verbose=False)
    collection = vector_store.load_collection("schema_tables")
    
    # Get all stored table data
    all_data = collection.get()
    
    print("📁 TABLE EMBEDDINGS ANALYSIS")
    print("=" * 50)
    
    if all_data and all_data.get("metadatas") and all_data.get("documents"):
        for i, (metadata, document) in enumerate(zip(all_data["metadatas"], all_data["documents"])):
            table_name = metadata.get("table", "unknown")
            print(f"\n{i+1}. Table: {table_name}")
            print(f"   Embedded text: {document[:200]}...")
            
            # Check for keywords that might cause false matches
            keywords = ["samsung", "product", "sold", "sale", "quantity", "campaign", "marketing"]
            found_keywords = []
            for keyword in keywords:
                if keyword.lower() in document.lower():
                    found_keywords.append(keyword)
            
            if found_keywords:
                print(f"   Keywords found: {', '.join(found_keywords)}")
            else:
                print(f"   Keywords found: None")

if __name__ == "__main__":
    try:
        examine_table_embeddings()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
