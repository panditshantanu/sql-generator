#!/usr/bin/env python3
"""
Setup script for SQL Generator embeddings.
Run this script to initialize the vector database with your schema.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main setup function."""
    print("🔧 SQL Generator - First Time Setup")
    print("=" * 50)
    
    try:
        from sql_generator.utils.config_manager import get_config
        from sql_generator.main import create_embeddings_and_store
        
        # Get configuration
        config = get_config()
        schema_path = config.get("schema.schema_path", "data/schemas/tables_schema.json")
        
        # Verify schema file exists
        schema_file = Path(schema_path)
        if not schema_file.exists():
            alt_path = project_root / schema_path
            if alt_path.exists():
                schema_path = str(alt_path)
            else:
                print(f"❌ Schema file not found: {schema_path}")
                print(f"❌ Also tried: {alt_path}")
                print("\nPlease check your schema file location.")
                return
        
        print(f"📁 Schema file: {schema_path}")
        print("\n🚀 Creating embeddings and setting up vector store...")
        print("This may take a few minutes depending on your schema size.")
        
        # Create embeddings
        result = create_embeddings_and_store(
            schema_path=schema_path,
            collection_prefix="schema",
            clear_existing=True
        )
        
        print("\n✅ Setup completed successfully!")
        print(f"📊 Results: {result}")
        
        print("\n🎉 You can now use the SQL Generator!")
        print("Try running:")
        print("  python quick_sql.py")
        print("  python run_sql_generator.py --interactive")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nPlease check your configuration and try again.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
