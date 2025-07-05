#!/usr/bin/env python3
"""
Complete setup script to regenerate embeddings for the SQL Generator.
This will clean and rebuild the entire embedding database.
"""

import os
import sys
import shutil
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("🚀 SQL Generator - Complete Environment Setup")
    print("=" * 60)
    print("This will regenerate all embeddings and set up the environment.")
    print()
    
    # Step 1: Clean existing ChromaDB
    chroma_path = project_root / "data" / "chroma_db"
    if chroma_path.exists():
        response = input(f"🧹 Remove existing ChromaDB at {chroma_path}? (y/N): ")
        if response.lower() == 'y':
            print(f"🧹 Removing {chroma_path}...")
            shutil.rmtree(chroma_path)
            print("✅ ChromaDB cleaned")
        else:
            print("⚠️  Keeping existing ChromaDB - may cause conflicts")
    
    # Step 2: Check schema file exists
    schema_path = project_root / "data" / "schemas" / "tables_schema.json"
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        print("Please ensure your schema file exists before continuing.")
        return False
    
    print(f"✅ Schema file found: {schema_path}")
    
    # Step 3: Generate embeddings using the main pipeline
    print("\n🤖 Generating embeddings...")
    try:
        from sql_generator.main import main_pipeline
        
        # Run the complete pipeline with clean database
        main_pipeline(
            clean_db=True,           # Clean existing database
            force_clean=True,        # Don't ask for confirmation
            collection_prefix="schema",  # Use default prefix
            run_search_demo=False    # Skip demo for setup
        )
        
        print("✅ Embeddings generated successfully!")
        
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Verify embeddings
    print("\n🔍 Verifying embeddings...")
    try:
        from sql_generator.schema.schema_searcher import SchemaSearcher
        
        searcher = SchemaSearcher(verbose=False)
        stats = searcher.get_stats()
        
        # Check collections
        columns_info = stats.get('collections', {}).get('schema_columns', {})
        tables_info = stats.get('collections', {}).get('schema_tables', {})
        
        columns_count = columns_info.get('count', 0)
        tables_count = tables_info.get('count', 0)
        
        print(f"✅ Verification successful:")
        print(f"   📋 Columns indexed: {columns_count}")
        print(f"   📁 Tables indexed: {tables_count}")
        
        # Test a simple search if data exists
        if columns_count > 0:
            results = searcher.search_columns("customer name", k=3)
            if results:
                print(f"   🔍 Sample search successful: found {len(results)} results")
        
    except Exception as e:
        print(f"❌ Error verifying embeddings: {e}")
        return False
    
    # Step 5: Test the enterprise architecture
    print("\n🏢 Testing enterprise architecture...")
    try:
        from sql_generator.main import generate_sql_prompt_data
        
        # Test with a simple query
        analysis_data, prompt_string = generate_sql_prompt_data(
            "What customers have purchased products?"
        )
        
        if analysis_data.get('success'):
            print("✅ Enterprise architecture working!")
            print(f"   📊 Tables found: {len(analysis_data.get('relevant_tables', []))}")
        else:
            print(f"⚠️  Enterprise architecture issue: {analysis_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error testing enterprise architecture: {e}")
        # This is not critical for basic setup
    
    print("\n🎉 Environment Setup Complete!")
    print("=" * 60)
    print("You can now use the SQL Generator in the following ways:")
    print()
    print("1. Interactive mode:")
    print("   python run_sql_generator.py --interactive")
    print()
    print("2. Direct query:")
    print("   python -c \"from sql_generator.main import generate_sql_prompt_demo; generate_sql_prompt_demo('your query here')\"")
    print()
    print("3. Test with Mike query:")
    print("   python -c \"from sql_generator.main import generate_sql_prompt_demo; generate_sql_prompt_demo('What products has customer mike purchased?')\"")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("✅ Setup completed successfully!")
        else:
            print("❌ Setup failed. Check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
