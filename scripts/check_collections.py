#!/usr/bin/env python3
"""
Check what collections exist in ChromaDB
"""

import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from schema.vector_store import VectorStore
    
    print("🔍 Checking ChromaDB collections...")
    vs = VectorStore()
    collections = vs.list_collections()
    
    print(f"📊 ChromaDB path: {vs.persist_dir}")
    print(f"📋 Available collections: {collections}")
    
    if not collections:
        print("\n❌ No collections found!")
        print("You need to create embeddings first. Run:")
        print("python main.py --mode embed --clean --force")
    else:
        print(f"\n✅ Found {len(collections)} collection(s)")
        for collection_name in collections:
            info = vs.get_collection_info(collection_name)
            print(f"   - {collection_name}: {info.get('count', 0)} records")

except Exception as e:
    print(f"❌ Error: {e}")
