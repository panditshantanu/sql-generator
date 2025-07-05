#!/usr/bin/env python3
"""
Quick Interactive SQL Generator Script.
Run this for immediate access to SQL generation with analysis.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main function to run the interactive SQL generator."""
    print("🚀 SQL Generator - Quick Start")
    print("=" * 50)
    
    try:
        from sql_generator import SQLGenerator
        from sql_generator.utils.config_manager import get_config
        
        # Initialize with default schema
        config = get_config()
        schema_path = config.get("schema.schema_path", "data/schemas/tables_schema.json")
        
        # Handle relative paths
        schema_path_obj = Path(schema_path)
        if not schema_path_obj.exists():
            # Try from project root
            alt_path = project_root / schema_path
            if alt_path.exists():
                schema_path = str(alt_path)
            else:
                print(f"❌ Schema file not found: {schema_path}")
                print(f"❌ Also tried: {alt_path}")
                print("\nPlease check your configuration or provide a valid schema path.")
                return
        
        print(f"📁 Loading schema from: {schema_path}")
        generator = SQLGenerator(schema_path=schema_path)
        print("✅ SQL Generator ready!")
        
        # Check if embeddings exist, if not offer to create them
        try:
            schema_info = generator.get_schema_info()
            searcher_stats = generator.searcher.get_stats()
            collections = searcher_stats.get('collections', {})
            
            # Check if collections exist and have data
            missing_collections = []
            for col_name, info in collections.items():
                if not info.get('exists', False) or info.get('count', 0) == 0:
                    missing_collections.append(col_name)
            
            if missing_collections:
                print(f"\n⚠️  Missing or empty collections: {', '.join(missing_collections)}")
                print("💡 Embeddings need to be initialized for the first time.")
                
                setup_choice = input("🔧 Would you like to set up embeddings now? (y/N): ").strip().lower()
                if setup_choice == 'y':
                    print("\n🔧 Setting up embeddings...")
                    from sql_generator.main import create_embeddings_and_store
                    
                    result = create_embeddings_and_store(
                        schema_path=schema_path,
                        collection_prefix="schema",
                        clear_existing=True
                    )
                    
                    print("✅ Embeddings setup completed!")
                    
                    # Reinitialize generator
                    generator = SQLGenerator(schema_path=schema_path)
                    print("🔄 SQL Generator reinitialized")
                else:
                    print("⚠️  Continuing without embeddings (queries may not work properly)")
        
        except Exception as e:
            print(f"⚠️  Could not check embedding status: {e}")
        
        print("\n💡 Examples you can try:")
        print("  • Show me all customers")
        print("  • Find orders from last month")
        print("  • Get customer details with their orders")
        print("  • Type 'quit' to exit")
        print("-" * 50)
        
        while True:
            try:
                query = input("\n💬 Enter your query: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if query.lower() == 'help':
                    print("\n📚 Available commands:")
                    print("  • Enter any natural language query")
                    print("  • 'schema' - Show schema information")
                    print("  • 'quit' - Exit the program")
                    continue
                
                if query.lower() == 'schema':
                    schema_info = generator.get_schema_info()
                    print(f"\n📊 Schema Info:")
                    print(f"   Tables: {schema_info.get('tables_count', 0)}")
                    print(f"   Columns: {schema_info.get('columns_count', 0)}")
                    continue
                
                # Generate SQL with analysis
                print(f"\n🔍 Processing: '{query}'")
                print("=" * 60)
                
                result = generator.generate_sql(query)
                
                # Show generated SQL
                print("\n📝 Generated SQL:")
                print("-" * 40)
                print(result.sql)
                print("-" * 40)
                
                # Show quick analysis
                print(f"\n📊 Confidence: {result.confidence:.2f}")
                
                search_results = result.metadata.get('search_results', [])
                if search_results:
                    print(f"🔍 Found {len(search_results)} relevant schema elements")
                    
                    # Show top 3 matches
                    print("\n🎯 Top matches:")
                    for i, match in enumerate(search_results[:3], 1):
                        score = match.get('score', 0)
                        content = match.get('content', '')[:60]
                        collection = match.get('collection_type', 'unknown')
                        print(f"   {i}. [{collection}] {score:.3f} - {content}...")
                
                tables_used = result.metadata.get('tables_used', [])
                if tables_used:
                    print(f"🗃️  Tables: {', '.join(tables_used)}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Please try again with a different query.")
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure the SQL Generator package is properly installed.")
    except Exception as e:
        print(f"❌ Failed to initialize SQL Generator: {e}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()
