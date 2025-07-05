#!/usr/bin/env python3
"""
Simple script to regenerate embeddings only.
Use this if you just want to rebuild the embeddings without full setup.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def regenerate_embeddings():
    """Regenerate embeddings using the existing pipeline."""
    print("🔄 Regenerating SQL Generator Embeddings")
    print("=" * 50)
    
    try:
        # Import and run the embedding generation
        from sql_generator.main import create_embeddings_and_store
        
        print("🤖 Starting embedding generation...")
        
        # Generate embeddings with clean slate
        results = create_embeddings_and_store(
            schema_path=None,  # Use path from config
            collection_prefix="schema",
            clear_existing=True  # Clear existing collections
        )
        
        print("\n✅ Embeddings regenerated successfully!")
        print(f"   📋 Columns processed: {results.get('columns', 0)}")
        print(f"   📁 Tables processed: {results.get('tables', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error regenerating embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_embeddings():
    """Verify that embeddings were created successfully."""
    print("\n🔍 Verifying embeddings...")
    
    try:
        from sql_generator.schema.schema_searcher import SchemaSearcher
        
        searcher = SchemaSearcher()
        
        # Get statistics
        stats = searcher.get_stats()
        
        # Check collections
        columns_info = stats.get('collections', {}).get('schema_columns', {})
        tables_info = stats.get('collections', {}).get('schema_tables', {})
        
        columns_count = columns_info.get('count', 0)
        tables_count = tables_info.get('count', 0)
        
        print(f"✅ Verification successful:")
        print(f"   📊 Columns: {columns_count} indexed")
        print(f"   📁 Tables: {tables_count} indexed") 
        
        # Quick search test if data exists
        if columns_count > 0:
            test_results = searcher.search_columns("customer", k=2)
            print(f"   🔍 Search test: {len(test_results)} results for 'customer'")
        
        return columns_count > 0 and tables_count > 0
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    # Step 1: Regenerate embeddings
    if not regenerate_embeddings():
        print("❌ Failed to regenerate embeddings")
        return False
    
    # Step 2: Verify embeddings
    if not verify_embeddings():
        print("❌ Failed to verify embeddings")
        return False
    
    print("\n🎉 Embedding regeneration complete!")
    print("\nYou can now test with:")
    print("  python run_sql_generator.py --interactive")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
