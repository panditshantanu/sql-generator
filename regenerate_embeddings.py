#!/usr/bin/env python3
"""
Manual embedding regeneration script.
Use this if the other methods don't work.
"""

import sys
from pathlib import Path
import shutil

# Add project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def regenerate_embeddings():
    """Manually regenerate embeddings."""
    print("🔧 Manual Embedding Regeneration")
    print("=" * 50)
    
    try:
        # Step 1: Clear existing ChromaDB data
        chroma_dir = project_root / "data" / "chroma_db"
        if chroma_dir.exists():
            print(f"🗑️  Removing existing ChromaDB data: {chroma_dir}")
            shutil.rmtree(chroma_dir)
            print("✅ Old data removed")
        else:
            print("ℹ️  No existing ChromaDB data found")
        
        # Step 2: Import and run embedding creation
        print("\n🚀 Creating new embeddings...")
        
        from sql_generator.main import create_embeddings_and_store
        
        schema_path = "data/schemas/tables_schema.json"
        if not (project_root / schema_path).exists():
            print(f"❌ Schema file not found: {schema_path}")
            return False
        
        result = create_embeddings_and_store(
            schema_path=schema_path,
            collection_prefix="schema",
            clear_existing=True
        )
        
        print("✅ Embeddings created successfully!")
        print(f"📊 Result: {result}")
        
        # Step 3: Verify embeddings work
        print("\n🧪 Testing embeddings...")
        
        from sql_generator.schema.schema_searcher import SchemaSearcher
        
        searcher = SchemaSearcher(verbose=False)
        test_results = searcher.search_tables("customer", n_results=3)
        
        if test_results and any(r.get('score', 0) > 0 for r in test_results):
            print("✅ Embeddings are working correctly!")
            
            print("\n📊 Sample results:")
            for i, result in enumerate(test_results[:2], 1):
                score = result.get('score', 0)
                metadata = result.get('metadata', {})
                table = metadata.get('table_name', 'unknown')
                print(f"   {i}. {table}: score {score:.4f}")
            
            return True
        else:
            print("❌ Embeddings test failed - all scores are still 0")
            return False
        
    except Exception as e:
        print(f"❌ Error during regeneration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = regenerate_embeddings()
    
    if success:
        print(f"\n🎉 Embedding regeneration completed successfully!")
        print(f"You can now run your queries normally.")
    else:
        print(f"\n❌ Embedding regeneration failed.")
        print(f"Check the error messages above for details.")
