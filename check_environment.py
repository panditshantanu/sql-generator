#!/usr/bin/env python3
"""
Check the current state of the SQL Generator environment.
Use this to see what needs to be set up.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_files():
    """Check if required files exist."""
    print("📁 Checking required files...")
    
    required_files = [
        "data/schemas/tables_schema.json",
        "data/config/config.json",
        "sql_generator/main.py",
        "sql_generator/schema/schema_searcher.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def check_chroma_db():
    """Check if ChromaDB exists and has data."""
    print("\n🗄️  Checking ChromaDB...")
    
    chroma_path = project_root / "data" / "chroma_db"
    if not chroma_path.exists():
        print("   ❌ ChromaDB directory not found - needs to be created")
        return False
    
    # Check if there are collections
    collection_dirs = [d for d in chroma_path.iterdir() if d.is_dir() and d.name != "__pycache__"]
    if not collection_dirs:
        print("   ⚠️  ChromaDB exists but appears empty")
        return False
    
    print(f"   ✅ ChromaDB found with {len(collection_dirs)} collections")
    return True

def check_embeddings():
    """Check if embeddings are working."""
    print("\n🤖 Checking embeddings...")
    
    try:
        from sql_generator.schema.schema_searcher import SchemaSearcher
        
        searcher = SchemaSearcher()
        stats = searcher.get_stats()
        
        # Check if collections exist and have data
        columns_info = stats.get('collections', {}).get('schema_columns', {})
        tables_info = stats.get('collections', {}).get('schema_tables', {})
        
        columns_count = columns_info.get('count', 0)
        tables_count = tables_info.get('count', 0)
        
        if columns_count > 0 and tables_count > 0:
            print(f"   ✅ Embeddings working:")
            print(f"      📋 {columns_count} columns indexed")
            print(f"      📁 {tables_count} tables indexed")
            return True
        else:
            print("   ❌ Embeddings exist but no data found")
            print(f"      📋 Columns: {columns_count}")
            print(f"      📁 Tables: {tables_count}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking embeddings: {e}")
        return False

def check_enterprise_architecture():
    """Check if the enterprise architecture is working."""
    print("\n🏢 Checking enterprise architecture...")
    
    try:
        from sql_generator.core.query_analyzer import QueryAnalyzer
        from sql_generator.core.schema_manager import SchemaManager
        
        # Test basic creation
        qa = QueryAnalyzer()
        config = {'min_confidence_threshold': 0.5, 'max_tables_per_query': 5, 'max_columns_per_table': 3, 'enable_context_filtering': True}
        sm = SchemaManager(qa, config)
        
        print("   ✅ Enterprise components working")
        return True
        
    except Exception as e:
        print(f"   ❌ Enterprise architecture error: {e}")
        return False

def main():
    print("🔍 SQL Generator Environment Status Check")
    print("=" * 50)
    
    # Check each component
    files_ok = check_files()
    chroma_ok = check_chroma_db()
    embeddings_ok = check_embeddings()
    enterprise_ok = check_enterprise_architecture()
    
    print("\n📊 Summary:")
    print(f"   📁 Required files: {'✅' if files_ok else '❌'}")
    print(f"   🗄️  ChromaDB: {'✅' if chroma_ok else '❌'}")
    print(f"   🤖 Embeddings: {'✅' if embeddings_ok else '❌'}")
    print(f"   🏢 Enterprise arch: {'✅' if enterprise_ok else '❌'}")
    
    print("\n🚀 Recommendations:")
    
    if not files_ok:
        print("   ❌ Missing required files - check project structure")
    
    if not chroma_ok or not embeddings_ok:
        print("   🔄 Run: python setup_environment.py")
        print("   🔄 Or: python regenerate_embeddings_only.py")
    
    if files_ok and chroma_ok and embeddings_ok and enterprise_ok:
        print("   🎉 Everything looks good! You can run:")
        print("      python run_sql_generator.py --interactive")
    
    if not enterprise_ok and embeddings_ok:
        print("   ⚠️  Embeddings work but enterprise architecture has issues")
        print("      Basic functionality should still work")

if __name__ == "__main__":
    main()
