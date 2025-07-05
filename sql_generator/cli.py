"""
Command Line Interface for SQL Generator.
Provides interactive commands for querying and analysis.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from .core import SQLGenerator, SQLResult
from .utils.config_manager import get_config


class SQLGeneratorCLI:
    """Command line interface for the SQL Generator."""
    
    def __init__(self, schema_path: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the CLI.
        
        Args:
            schema_path: Path to schema file
            config_path: Path to config file
        """
        self.config = get_config()
        
        # Set up schema path with better defaults
        if schema_path is None:
            schema_path = self.config.get("schema.schema_path", "data/schemas/tables_schema.json")
        
        # Handle relative paths from project root
        self.schema_path = Path(schema_path)
        if not self.schema_path.exists():
            # Try from project root
            project_root = Path(__file__).parent.parent
            alt_schema_path = project_root / schema_path
            if alt_schema_path.exists():
                self.schema_path = alt_schema_path
            else:
                print(f"❌ Schema file not found at: {schema_path}")
                if alt_schema_path != self.schema_path:
                    print(f"❌ Also tried: {alt_schema_path}")
                print("\n💡 Available schema files:")
                self._show_available_schemas()
                print("\nPlease provide a valid schema path or update your config.")
                sys.exit(1)
        
        # Initialize SQL Generator
        try:
            self.generator = SQLGenerator(schema_path=str(self.schema_path))
            print(f"✅ SQL Generator initialized with schema: {self.schema_path}")
        except Exception as e:
            print(f"❌ Failed to initialize SQL Generator: {e}")
            sys.exit(1)
    
    def generate_sql(self, query: str, show_analysis: bool = False, show_prompt: bool = False) -> SQLResult:
        """
        Generate SQL from natural language query.
        
        Args:
            query: Natural language query
            show_analysis: Whether to show detailed analysis
            show_prompt: Whether to show the generated prompt
            
        Returns:
            SQLResult object
        """
        print(f"\n🔍 Processing query: '{query}'")
        print("=" * 60)
        
        try:
            # Generate SQL
            result = self.generator.generate_sql(query)
            
            # Display prompt if requested
            if show_prompt and result.prompt:
                self.show_prompt(result.prompt)
            
            # Display the generated prompt (which is in the sql field)
            print("\n� Generated Prompt for LLM:")
            print("-" * 40)
            print(result.sql)
            print("-" * 40)
            
            if show_analysis:
                self.show_detailed_analysis(result)
            
            return result
            
        except Exception as e:
            print(f"❌ Error generating SQL: {e}")
            return SQLResult(sql="-- Error occurred during generation", confidence=0.0)
    
    def show_prompt(self, prompt: str):
        """
        Display the generated prompt.
        
        Args:
            prompt: The prompt that was generated for the LLM
        """
        print("\n📋 Generated Prompt:")
        print("=" * 60)
        print(prompt)
        print("=" * 60)
    
    def show_detailed_analysis(self, result: SQLResult):
        """
        Show detailed analysis of the SQL generation.
        
        Args:
            result: SQLResult object to analyze
        """
        print("\n🔬 Detailed Analysis:")
        print("=" * 60)
        
        # Basic metrics
        print(f"📊 Confidence Score: {result.confidence:.2f}")
        print(f"📏 Query Length: {result.metadata.get('query_length', 'N/A')} characters")
        
        # Tables identified and selection reasoning
        tables_used = result.metadata.get('tables_used', [])
        search_results = result.metadata.get('search_results', [])
        
        print(f"\n🗃️  Table Selection Analysis:")
        print("-" * 40)
        
        if tables_used:
            print(f"✅ Tables Selected: {', '.join(tables_used)}")
            
            # Calculate and show table relevance scores
            table_scores = {}
            table_reasons = {}
            
            # Analyze why each table was selected
            for search_result in search_results:
                metadata = search_result.get('metadata', {})
                table_name = metadata.get('table_name', metadata.get('table'))
                if table_name and table_name in tables_used:
                    score = search_result.get('score', 0.0)
                    if table_name not in table_scores:
                        table_scores[table_name] = []
                        table_reasons[table_name] = []
                    table_scores[table_name].append(score)
                    
                    # Extract the reason (content that matched)
                    content = search_result.get('content', '')[:50]
                    table_reasons[table_name].append(content)
            
            print("\n📊 Table Selection Details:")
            for table in tables_used:
                if table in table_scores and table_scores[table]:
                    scores = table_scores[table]
                    avg_score = sum(scores) / len(scores)
                    best_score = max(scores)
                    match_count = len(scores)
                    
                    print(f"\n   🗃️  {table}:")
                    print(f"      • Selection Method: Schema vector search")
                    print(f"      • Average Relevance: {avg_score:.3f}")
                    print(f"      • Best Score: {best_score:.3f}")
                    print(f"      • Total Matches: {match_count}")
                    
                    # Show top reasons
                    unique_reasons = list(set(table_reasons[table]))[:2]
                    if unique_reasons:
                        print(f"      • Key Matches: {', '.join(unique_reasons)}...")
                else:
                    print(f"\n   🗃️  {table}:")
                    print(f"      • Selection Method: Keyword inference from query")
                    print(f"      • Relevance: Inferred from query terms")
        else:
            print("❌ No tables were selected for this query")
            print("� This might indicate:")
            print("   • Query terms don't match known tables/columns")
            print("   • Vector embeddings need to be regenerated")
            print("   • Schema might not contain relevant information")
            print("\n🔧 Try:")
            print("   • More specific table/column names")
            print("   • Different query phrasing")
            print("   • Run 'setup' to rebuild embeddings")
        
        # Search results analysis - Enhanced version
        search_results = result.metadata.get('search_results', [])
        if search_results:
            print(f"\n🔍 Schema Search Results ({len(search_results)} found):")
            print("=" * 60)
            
            # Create detailed analysis of each search result
            table_matches = {}
            column_matches = {}
            
            for i, search_result in enumerate(search_results, 1):
                score = search_result.get('score', 0.0)
                content = search_result.get('content', 'No content')
                metadata = search_result.get('metadata', {})
                
                # Extract metadata fields
                table_name = metadata.get('table_name', metadata.get('table', 'Unknown'))
                column_name = metadata.get('column', '')
                collection_type = metadata.get('collection_type', metadata.get('level', 'unknown'))
                
                print(f"\n🔍 Match #{i}: {collection_type.upper()} | Score: {score:.3f}")
                
                if column_name:
                    print(f"   📊 Column: {table_name}.{column_name}")
                    if table_name not in column_matches:
                        column_matches[table_name] = []
                    column_matches[table_name].append({
                        'column': column_name,
                        'score': score,
                        'content': content
                    })
                else:
                    print(f"   📋 Table: {table_name}")
                    if table_name not in table_matches:
                        table_matches[table_name] = []
                    table_matches[table_name].append({
                        'score': score,
                        'content': content
                    })
                
                # Show the content that matched
                truncated_content = content[:100] + "..." if len(content) > 100 else content
                print(f"   💭 Matched Content: {truncated_content}")
                
                # Show why it matched (extract key terms)
                query_words = result.metadata.get('original_query', '').lower().split()
                matching_words = []
                content_lower = content.lower()
                for word in query_words:
                    if len(word) > 2 and word in content_lower:
                        matching_words.append(word)
                
                if matching_words:
                    print(f"   🎯 Key Matches: {', '.join(matching_words)}")
                
                print()
            
            # Summary by table
            if table_matches or column_matches:
                print("\n📊 Summary by Table:")
                print("-" * 40)
                
                all_tables = set(table_matches.keys()) | set(column_matches.keys())
                for table in sorted(all_tables):
                    table_scores = []
                    column_count = 0
                    
                    if table in table_matches:
                        table_scores.extend([match['score'] for match in table_matches[table]])
                    
                    if table in column_matches:
                        column_count = len(column_matches[table])
                        table_scores.extend([match['score'] for match in column_matches[table]])
                    
                    if table_scores:
                        avg_score = sum(table_scores) / len(table_scores)
                        max_score = max(table_scores)
                        
                        print(f"   🗃️  {table}:")
                        print(f"      • Average Score: {avg_score:.3f}")
                        print(f"      • Best Score: {max_score:.3f}")
                        print(f"      • Total Matches: {len(table_scores)}")
                        if column_count > 0:
                            print(f"      • Column Matches: {column_count}")
                        print()
        else:
            print("\n🔍 Schema Search Results: No relevant schema elements found")
        
        # Prompt Analysis (since we're generating prompts, not SQL)
        self.analyze_prompt_structure(result.sql)
    
    def analyze_prompt_structure(self, prompt: str):
        """
        Analyze the structure of the generated prompt.
        
        Args:
            prompt: Generated prompt to analyze
        """
        print("\n⚙️  Prompt Structure Analysis:")
        print("-" * 40)
        
        # Prompt type detection
        if "expert SQL generator" in prompt.lower():
            if "relationships" in prompt.lower():
                prompt_type = "Advanced (with relationships)"
            elif "aggregate" in prompt.lower() or "analytical" in prompt.lower():
                prompt_type = "Analytics (aggregation focused)"
            else:
                prompt_type = "Basic (standard SQL generation)"
        else:
            prompt_type = "Custom/Fallback"
        
        print(f"📝 Prompt Type: {prompt_type}")
        
        # Content analysis
        sections = []
        if "Database Schema:" in prompt:
            sections.append("Database Schema")
        if "Table Relationships:" in prompt:
            sections.append("Table Relationships")
        if "Instructions:" in prompt:
            sections.append("Generation Instructions")
        if "Context:" in prompt:
            sections.append("Query Context")
        
        print(f"� Prompt Sections: {', '.join(sections)}")
        
        # Schema content stats
        lines = prompt.split('\n')
        schema_lines = [line for line in lines if line.strip().startswith(('Table:', '  Description:', '    -'))]
        table_count = len([line for line in lines if line.strip().startswith('Table:')])
        column_count = len([line for line in lines if line.strip().startswith('    -')])
        
        print(f"� Schema Content: {table_count} tables, {column_count} columns")
        print(f"📏 Prompt Length: {len(prompt)} characters")
        
    
    def show_schema_info(self):
        """Display information about the loaded schema."""
        print("\n📊 Schema Information:")
        print("=" * 60)
        
        schema_info = self.generator.get_schema_info()
        
        if 'error' in schema_info:
            print(f"❌ Error getting schema info: {schema_info['error']}")
            return
        
        print(f"📁 Schema File: {schema_info.get('schema_path', 'Unknown')}")
        print(f"🗃️  Total Tables: {schema_info.get('tables_count', 0)}")
        print(f"📋 Total Columns: {schema_info.get('columns_count', 0)}")
        
        # Show searcher stats if available
        try:
            searcher_stats = self.generator.searcher.get_stats()
            print(f"\n🤖 Search Index Status:")
            print(f"   Model: {searcher_stats.get('model_name', 'Unknown')}")
            
            collections = searcher_stats.get('collections', {})
            for collection_name, info in collections.items():
                status = "✅" if info.get('exists', False) else "❌"
                count = info.get('count', 0)
                print(f"   {status} {collection_name}: {count} items")
                
        except Exception as e:
            print(f"⚠️  Could not get search index stats: {e}")
    
    def interactive_mode(self):
        """Start interactive mode for querying."""
        print("\n🚀 SQL Generator - Interactive Mode")
        print("=" * 60)
        print("Commands:")
        print("  • Enter a natural language query to generate LLM prompt")
        print("  • Type 'analyze' + query for detailed analysis")
        print("  • Type 'prompt' + query to see the generated prompt")
        print("  • Type 'both' + query to see both prompt and analysis")
        print("  • Type 'setup' to initialize embeddings (first-time setup)")
        print("  • Type 'schema' to see schema information")
        print("  • Type 'help' for this help message")
        print("  • Type 'quit' or 'exit' to exit")
        print("=" * 60)
        print("Note: This generates prompts for LLM consumption, not actual SQL queries.")
        
        while True:
            try:
                user_input = input("\n💬 Enter your query: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    print("\n📚 Help:")
                    print("  • Natural language: 'Show me all customers from New York'")
                    print("  • With analysis: 'analyze Show me customer orders'")
                    print("  • With prompt: 'prompt Show me customer orders'")
                    print("  • With both: 'both Show me customer orders'")
                    print("  • Setup embeddings: 'setup' (run this first if you get collection errors)")
                    print("  • Schema info: 'schema'")
                    print("  • Exit: 'quit' or 'exit'")
                    print("\n💡 The system generates prompts for LLM consumption, not actual SQL.")
                
                elif user_input.lower() == 'setup':
                    self.setup_embeddings()
                
                elif user_input.lower() == 'schema':
                    self.show_schema_info()
                
                elif user_input.lower().startswith('analyze '):
                    query = user_input[8:].strip()
                    if query:
                        self.generate_sql(query, show_analysis=True)
                    else:
                        print("❌ Please provide a query after 'analyze'")
                
                elif user_input.lower().startswith('prompt '):
                    query = user_input[7:].strip()
                    if query:
                        self.generate_sql(query, show_prompt=True)
                    else:
                        print("❌ Please provide a query after 'prompt'")
                
                elif user_input.lower().startswith('both '):
                    query = user_input[5:].strip()
                    if query:
                        self.generate_sql(query, show_analysis=True, show_prompt=True)
                    else:
                        print("❌ Please provide a query after 'both'")
                
                else:
                    # Regular query
                    self.generate_sql(user_input, show_analysis=False)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
    
    def _show_available_schemas(self):
        """Show available schema files to help users."""
        try:
            project_root = Path(__file__).parent.parent
            schema_dirs = [
                project_root / "data" / "schemas",
                project_root / "schemas",
                Path(".")
            ]
            
            found_schemas = []
            for schema_dir in schema_dirs:
                if schema_dir.exists():
                    for ext in ["*.json", "*.pkl"]:
                        found_schemas.extend(schema_dir.glob(ext))
            
            if found_schemas:
                for schema_file in found_schemas:
                    rel_path = schema_file.relative_to(project_root) if schema_file.is_relative_to(project_root) else schema_file
                    print(f"   - {rel_path}")
            else:
                print("   No schema files found in common locations")
                
        except Exception:
            print("   Could not scan for schema files")
    
    def setup_embeddings(self):
        """Initialize embeddings and vector store for first-time use."""
        print("\n🔧 Setting up embeddings and vector store...")
        print("=" * 60)
        
        try:
            # Try different import approaches
            try:
                from .main import create_embeddings_and_store
            except ImportError:
                try:
                    from main import create_embeddings_and_store
                except ImportError:
                    from sql_generator.main import create_embeddings_and_store
            
            # Use the schema path from our generator
            result = create_embeddings_and_store(
                schema_path=str(self.schema_path),
                collection_prefix="schema",
                clear_existing=True
            )
            
            print("✅ Embeddings setup completed successfully!")
            print(f"📊 Results: {result}")
            
            # Reinitialize the generator to pick up new embeddings
            self.generator = SQLGenerator(schema_path=str(self.schema_path))
            print("🔄 SQL Generator reinitialized with new embeddings")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup embeddings: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="SQL Generator - Natural Language to SQL Conversion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m sql_generator.cli --query "Show me all customers"
  python -m sql_generator.cli --query "Find orders from last month" --analyze
  python -m sql_generator.cli --interactive
  python -m sql_generator.cli --schema-info
        """
    )
    
    parser.add_argument(
        '--schema-path', '-s',
        type=str,
        help='Path to schema JSON file'
    )
    
    parser.add_argument(
        '--config-path', '-c',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Natural language query to convert to SQL'
    )
    
    parser.add_argument(
        '--analyze', '-a',
        action='store_true',
        help='Show detailed analysis of the generation process'
    )
    
    parser.add_argument(
        '--show-prompt', '-p',
        action='store_true',
        help='Show the generated prompt that would be sent to the LLM (same as main output now)'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Start interactive mode'
    )
    
    parser.add_argument(
        '--schema-info',
        action='store_true',
        help='Show information about the loaded schema'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Initialize embeddings and vector store (first-time setup)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    try:
        # Initialize CLI
        cli = SQLGeneratorCLI(
            schema_path=args.schema_path,
            config_path=args.config_path
        )
        
        # Handle different modes
        if args.interactive:
            cli.interactive_mode()
        
        elif args.setup:
            cli.setup_embeddings()
        
        elif args.schema_info:
            cli.show_schema_info()
        
        elif args.query:
            cli.generate_sql(args.query, show_analysis=args.analyze, show_prompt=args.show_prompt)
        
        else:
            # Default to interactive mode if no specific action
            print("No specific action provided. Starting interactive mode...")
            cli.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
