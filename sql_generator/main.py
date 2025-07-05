"""
Main module for the SQL Generator project.
Handles schema processing, embedding generation, and vector storage.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import Optional

# Add paths for robust imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

# Import new class-based components with robust fallback
try:
    # Try package-relative imports first
    from .schema.semantic_schema import SemanticSchema
    from .schema.schema_embedder import SchemaEmbedder
    from .schema.vector_store import VectorStore
    from .schema.schema_searcher import SchemaSearcher
    from .utils.config_manager import get_config
except ImportError:
    try:
        # Try direct imports from current directory
        from schema.semantic_schema import SemanticSchema
        from schema.schema_embedder import SchemaEmbedder
        from schema.vector_store import VectorStore
        from schema.schema_searcher import SchemaSearcher
        from utils.config_manager import get_config
    except ImportError:
        # Try absolute imports
        from sql_generator.schema.semantic_schema import SemanticSchema
        from sql_generator.schema.schema_embedder import SchemaEmbedder
        from sql_generator.schema.vector_store import VectorStore
        from sql_generator.schema.schema_searcher import SchemaSearcher
        from sql_generator.utils.config_manager import get_config
    from utils.config_manager import get_config


def setup_logging():
    """Setup logging configuration."""
    config = get_config()
    log_level = config.get("logging.level", "INFO")
    log_format = config.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format
    )


def clean_chroma_db(persist_dir: str, force: bool = False) -> bool:
    """
    Clean existing ChromaDB directory.
    
    Args:
        persist_dir: Path to ChromaDB directory
        force: If True, removes without confirmation
        
    Returns:
        True if cleaned, False if skipped
    """
    persist_path = Path(persist_dir)
    
    if persist_path.exists():
        if not force:
            response = input(f"🧹 ChromaDB directory '{persist_dir}' exists. Remove it? (y/N): ")
            if response.lower() != 'y':
                print("Keeping existing ChromaDB directory.")
                return False
        
        print(f"🧹 Removing existing ChromaDB directory: {persist_dir}")
        shutil.rmtree(persist_path)
        return True
    
    return False


def create_embeddings_and_store(
    schema_path: Optional[str] = None,
    collection_prefix: str = "schema",
    clear_existing: bool = True
) -> dict:
    """
    Create embeddings from schema and store in ChromaDB.
    
    Args:
        schema_path: Path to schema JSON file (uses config if None)
        collection_prefix: Prefix for collection names
        clear_existing: Whether to clear existing collections
        
    Returns:
        Dictionary with storage results
    """
    config = get_config()
    
    # Use provided schema path or get from config
    if schema_path is None:
        schema_path = config.get("schema.schema_path")
    
    if not schema_path or not Path(schema_path).exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    print("🚀 Starting schema embedding and storage process...")
    print(f"📄 Schema file: {schema_path}")
    
    # Step 1: Load and prepare semantic schema
    print("\n📋 Step 1: Loading semantic schema...")
    semantic_schema = SemanticSchema(schema_path)
    semantic_data = semantic_schema.prepare_semantic_data()
    
    print(f"✅ Loaded {len(semantic_data['columns'])} columns and {len(semantic_data['tables'])} tables")
    
    # Step 2: Generate embeddings
    print("\n🤖 Step 2: Generating embeddings...")
    embedder = SchemaEmbedder()
    embedded_data = embedder.embed_semantic_data(semantic_data, cache_prefix="retail_schema")
    
    # Step 3: Store in vector database
    print("\n💾 Step 3: Storing in ChromaDB...")
    vector_store = VectorStore()
    results = vector_store.store_embedded_schema(
        embedded_data,
        collection_prefix=collection_prefix,
        clear_existing=clear_existing
    )
    
    print(f"✅ Storage completed:")
    print(f"   - Columns: {results.get('columns', 0)} records")
    print(f"   - Tables: {results.get('tables', 0)} records")
    print(f"   - ChromaDB path: {vector_store.persist_dir}")
    
    return results


def search_schema_demo(collection_prefix: str = "schema"):
    """
    Demonstrate schema search capabilities.
    
    Args:
        collection_prefix: Prefix for collection names
    """
    print("\n🔍 Schema Search Demo")
    print("=" * 50)
    
    try:
        # Initialize searcher
        searcher = SchemaSearcher(verbose=True)
        
        # Get search statistics
        print("\n📊 Search Statistics:")
        stats = searcher.get_search_stats()
        print(f"   - Columns: {stats['columns']['count']} (dim: {stats['columns']['embedding_dim']})")
        print(f"   - Tables: {stats['tables']['count']} (dim: {stats['tables']['embedding_dim']})")
        print(f"   - Available tables: {', '.join(stats['available_tables'][:5])}")
        
        # Test queries
        test_queries = [
            "total count of configurations stored in the database",
            "customer identification and contact information",
            "product inventory and stock levels"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Searching for: '{query}'")
            print("-" * 60)
            
            # Search columns
            print("📋 Top Column Matches:")
            column_results = searcher.search_columns(query, k=3)
            for i, result in enumerate(column_results, 1):
                table = result.get('table', 'unknown')
                column = result.get('column', 'unknown')
                score = result.get('score', 0)
                text = result.get('text', '')
                print(f"  {i}. {table}.{column} (score: {score:.3f})")
                print(f"     └─ {text[:80]}{'...' if len(text) > 80 else ''}")
            
            # Search tables
            print("\n📁 Top Table Matches:")
            table_results = searcher.search_tables(query, k=2)
            for i, result in enumerate(table_results, 1):
                table = result.get('table', 'unknown')
                score = result.get('score', 0)
                text = result.get('text', '')
                print(f"  {i}. {table} (score: {score:.3f})")
                print(f"     └─ {text[:100]}{'...' if len(text) > 100 else ''}")
        
        # Demonstrate table-specific search
        available_tables = searcher.get_available_tables()
        if available_tables:
            print(f"\n🏢 Table-Specific Search Demo ('{available_tables[0]}'):")
            table_results = searcher.search_by_table(
                available_tables[0], 
                "identification key", 
                k=3
            )
            for i, result in enumerate(table_results, 1):
                column = result.get('column', 'unknown')
                score = result.get('score', 0)
                print(f"  {i}. {column} (score: {score:.3f})")
        
    except Exception as e:
        print(f"❌ Search demo failed: {e}")
        print("Make sure embeddings are created first by running create_embeddings_and_store()")


def normalize_score(score: float, min_score: float = 0.0, max_score: float = 1.0) -> float:
    """
    Convert raw similarity score to confidence percentage using absolute thresholds.
    
    For semantic similarity scores (0.0 to 1.0), we use empirically determined thresholds:
    - 0.8+ = Very high confidence (90-100%)
    - 0.6-0.8 = High confidence (70-90%)  
    - 0.4-0.6 = Medium confidence (40-70%)
    - 0.2-0.4 = Low confidence (10-40%)
    - 0.0-0.2 = Very low confidence (0-10%)
    
    This avoids the problem of relative normalization where poor matches
    get artificially high confidence scores.
    """
    # Handle negative scores (clamp to 0)
    if score < 0:
        score = 0.0
    
    # Use absolute thresholds for semantic similarity scores
    if score >= 0.8:
        # Very high confidence: 90-100%
        # For scores > 1.0, give them 100% confidence
        if score > 1.0:
            return 100.0
        return 90 + ((score - 0.8) / 0.2) * 10
    elif score >= 0.6:
        # High confidence: 70-90%
        return 70 + ((score - 0.6) / 0.2) * 20
    elif score >= 0.4:
        # Medium confidence: 40-70%
        return 40 + ((score - 0.4) / 0.2) * 30
    elif score >= 0.2:
        # Low confidence: 10-40%
        return 10 + ((score - 0.2) / 0.2) * 30
    else:
        # Very low confidence: 0-10%
        return (score / 0.2) * 10


def filter_and_rank_results(results: list, min_confidence: float = 5.0) -> dict:
    """
    Filter low-confidence results and rank by quality.
    
    Args:
        results: List of search results with scores
        min_confidence: Minimum confidence threshold (0-100)
        
    Returns:
        Dictionary with filtered results categorized by confidence
    """
    if not results:
        return {"high": [], "medium": [], "low": [], "all_filtered": []}
    
    # Filter and categorize results using absolute confidence thresholds
    high_confidence = []    # 70-100%
    medium_confidence = []  # 30-70%
    low_confidence = []     # min_confidence-30%
    filtered_results = []   # All results above threshold
    
    for result in results:
        raw_score = result.get('score', 0)
        confidence = normalize_score(raw_score)  # Use absolute scoring, no min/max needed
        
        # Skip very low confidence results
        if confidence < min_confidence:
            continue
            
        # Add normalized confidence to result
        result_copy = result.copy()
        result_copy['confidence'] = confidence
        result_copy['raw_score'] = raw_score
        filtered_results.append(result_copy)
        
        # Categorize by confidence level
        if confidence >= 70:
            high_confidence.append(result_copy)
        elif confidence >= 30:
            medium_confidence.append(result_copy)
        else:
            low_confidence.append(result_copy)
    
    # Sort each category by confidence (descending)
    for category in [high_confidence, medium_confidence, low_confidence, filtered_results]:
        category.sort(key=lambda x: x['confidence'], reverse=True)
    
    return {
        "high": high_confidence,
        "medium": medium_confidence,
        "low": low_confidence,
        "all_filtered": filtered_results
    }


def display_ranked_results(ranked_results: dict, result_type: str = "columns"):
    """Display results with confidence-based ranking and filtering."""
    all_results = ranked_results["all_filtered"]
    
    if not all_results:
        print(f"   ❌ No {result_type} found above confidence threshold")
        return
    
    print(f"   📊 Found {len(all_results)} relevant {result_type}:")
    
    # Display high confidence results
    if ranked_results["high"]:
        print(f"\n   🎯 HIGH CONFIDENCE ({len(ranked_results['high'])} results):")
        for i, result in enumerate(ranked_results["high"], 1):
            _display_single_result(result, i, result_type, "🟢")
    
    # Display medium confidence results
    if ranked_results["medium"]:
        print(f"\n   🔍 MEDIUM CONFIDENCE ({len(ranked_results['medium'])} results):")
        for i, result in enumerate(ranked_results["medium"], 1):
            _display_single_result(result, i, result_type, "🟡")
    
    # Display low confidence results (if any)
    if ranked_results["low"]:
        print(f"\n   ⚠️  LOW CONFIDENCE ({len(ranked_results['low'])} results):")
        for i, result in enumerate(ranked_results["low"], 1):
            _display_single_result(result, i, result_type, "🔴")


def _display_single_result(result: dict, index: int, result_type: str, icon: str):
    """Helper to display a single search result."""
    confidence = result.get('confidence', 0)
    text = result.get('text', '')
    
    if result_type == "columns":
        table = result.get('table', 'unknown')
        column = result.get('column', 'unknown')
        print(f"      {icon} {index}. {table}.{column} ({confidence:.1f}% confidence)")
    else:  # tables
        table = result.get('table', 'unknown')
        print(f"      {icon} {index}. {table} ({confidence:.1f}% confidence)")
    
    # Truncate long text for readability
    display_text = text[:100] + "..." if len(text) > 100 else text
    print(f"         └─ {display_text}")


def custom_search_demo(query: str, collection_prefix: str = "schema"):
    """
    Run a custom search query and display detailed results with improved ranking.
    
    Args:
        query: The search query to test
        collection_prefix: Prefix for collection names
    """
    print(f"\n� Custom Search Query: '{query}'")
    print("=" * 80)
    
    try:
        # Initialize searcher
        searcher = SchemaSearcher(verbose=True)
        
        # Combined search with more results for better filtering
        print("🎯 Intelligent Schema Search Results:")
        combined_results = searcher.search_schema(query, k_columns=10, k_tables=5)
        
        # Filter and rank column results
        print(f"\n📋 COLUMN MATCHES:")
        column_ranked = filter_and_rank_results(
            combined_results["columns"], 
            min_confidence=30.0  # Slightly lower for analysis to show more detail
        )
        display_ranked_results(column_ranked, "columns")
        
        # Filter and rank table results  
        print(f"\n📁 TABLE MATCHES:")
        table_ranked = filter_and_rank_results(
            combined_results["tables"],
            min_confidence=30.0  # Slightly lower for analysis to show more detail
        )
        display_ranked_results(table_ranked, "tables")
        
        # Generate intelligent summary and recommendations
        print("\n🧠 INTELLIGENT ANALYSIS:")
        _generate_search_summary(column_ranked, table_ranked, query, searcher)
        
    except Exception as e:
        print(f"❌ Custom search failed: {e}")
        print("Make sure embeddings are created first!")


def _generate_search_summary(column_ranked: dict, table_ranked: dict, query: str, searcher):
    """Generate an intelligent summary of search results."""
    
    # Get best matches
    best_columns = column_ranked["high"] + column_ranked["medium"]
    best_tables = table_ranked["high"] + table_ranked["medium"]
    
    if not best_columns and not best_tables:
        print("   ❌ No high-confidence matches found. Try rephrasing your query.")
        return
    
    # Identify key tables
    relevant_tables = set()
    for result in best_columns[:5]:
        relevant_tables.add(result.get('table', ''))
    
    for result in best_tables[:3]:
        relevant_tables.add(result.get('table', ''))
    
    print(f"   🎯 Query Analysis: '{query}'")
    print(f"   📊 Key Tables Identified: {', '.join(sorted(relevant_tables)) if relevant_tables else 'None'}")
    
    if best_columns:
        top_column = best_columns[0]
        print(f"   🥇 Best Column Match: {top_column.get('table')}.{top_column.get('column')} ({top_column.get('confidence', 0):.1f}%)")
    
    if best_tables:
        top_table = best_tables[0]
        print(f"   🏆 Best Table Match: {top_table.get('table')} ({top_table.get('confidence', 0):.1f}%)")
    
    # Show suggested SQL approach
    if relevant_tables:
        print(f"\n   💡 Suggested SQL Approach:")
        if len(relevant_tables) == 1:
            table = list(relevant_tables)[0]
            print(f"      - Focus on table: {table}")
            if best_columns:
                key_cols = [r.get('column') for r in best_columns[:3] if r.get('table') == table]
                if key_cols:
                    print(f"      - Key columns: {', '.join(key_cols)}")
        else:
            print(f"      - Consider JOINs between: {', '.join(sorted(relevant_tables))}")
            
        # Show confidence summary
        total_results = len(column_ranked["all_filtered"]) + len(table_ranked["all_filtered"])
        high_conf = len(column_ranked["high"]) + len(table_ranked["high"])
        print(f"\n   📈 Confidence Summary: {high_conf}/{total_results} high-confidence matches")
        
        if high_conf == 0:
            print("      ⚠️  Consider rephrasing your query for better matches")


def generate_sql_prompt_demo(query: str, collection_prefix: str = "schema"):
    """
    Generate SQL prompt using enterprise-grade configurable components.
    
    Args:
        query: The user's natural language query
        collection_prefix: Prefix for collection names
    """
    print(f"\n🚀 SQL Prompt Generation for: '{query}'")
    print("=" * 80)
    
    try:
        # Use the enterprise-grade function
        analysis_data, prompt_string = generate_sql_prompt_data(query, collection_prefix)
        
        if not analysis_data["success"]:
            print(f"❌ Error: {analysis_data['error']}")
            return
        
        print("🔍 Step 1: Enterprise Query Analysis")
        print(f"   � Table Selection: {analysis_data.get('table_selection_reasoning', 'N/A')}")
        print(f"   📋 Column Selection: {analysis_data.get('column_selection_reasoning', 'N/A')}")
        
        if analysis_data.get("excluded_tables"):
            print(f"   🚫 Excluded Tables: {', '.join(analysis_data['excluded_tables'])}")
        
        relevant_tables = analysis_data["relevant_tables"]
        print(f"   ✅ Selected Tables ({len(relevant_tables)}): {', '.join(relevant_tables)}")
        
        if not relevant_tables:
            print("   ❌ No relevant tables found. Cannot generate SQL prompt.")
            return
        
        # Step 2: Display SQL prompt
        print(f"\n🤖 Step 2: Generated SQL Prompt")
        print("   ✅ SQL Prompt Generated Successfully!")
        
        # Step 3: Display the complete prompt
        print(f"\n📋 COMPLETE SQL GENERATION PROMPT:")
        print("=" * 60)
        print(prompt_string)
        print("=" * 60)
        
        # Step 4: Show suggested usage
        print(f"\n💡 HOW TO USE THIS PROMPT:")
        print("   1. Copy the above prompt")
        print("   2. Send it to your LLM (ChatGPT, Claude, etc.)")
        print("   3. The LLM will generate the SQL query")
        print("   4. Review and test the generated SQL")
        
        # Step 5: Show the analysis context
        print(f"\n🔍 ANALYSIS CONTEXT:")
        summary = analysis_data["summary"]
        print(f"   📊 Tables Found: {summary['total_tables_found']}")
        print(f"   📋 High-Confidence Columns: {summary['high_confidence_columns']}")
        print(f"   📁 High-Confidence Tables: {summary['high_confidence_tables']}")
        
        high_cols = analysis_data["column_results"]["high_confidence"]
        if high_cols:
            print("   🎯 Top Columns:")
            for col in high_cols[:3]:
                table = col.get('table', 'unknown')
                column = col.get('column', 'unknown')
                confidence = col.get('confidence', 0)
                print(f"      • {table}.{column} ({confidence:.1f}%)")
        
        high_tbls = analysis_data["table_results"]["high_confidence"] 
        if high_tbls:
            print("   🏆 Top Tables:")
            for tbl in high_tbls[:3]:
                table = tbl.get('table', 'unknown')
                confidence = tbl.get('confidence', 0)
                print(f"      • {table} ({confidence:.1f}%)")
        
    except Exception as e:
        print(f"❌ SQL prompt generation failed: {e}")
        import traceback
        traceback.print_exc()


def generate_sql_prompt_data(query: str, collection_prefix: str = "schema") -> tuple:
    """
    Generate SQL prompt and return structured data + prompt string.
    Simple approach focused on basic table selection to reduce prompt context.
    
    Args:
        query: The user's natural language query
        collection_prefix: Prefix for collection names
        
    Returns:
        Tuple of (analysis_data, prompt_string) where:
        - analysis_data: Dictionary with confidence scores, tables, columns, and analysis
        - prompt_string: The complete SQL generation prompt ready for LLM
    """
    try:
        # Step 1: Get semantic search results
        searcher = SchemaSearcher(verbose=True)
        combined_results = searcher.search_schema(query, k_columns=10, k_tables=5)
        
        # Step 2: Simple table selection 
        try:
            from simple_table_selector import SimpleTableSelector
            selector = SimpleTableSelector()
            selected_tables = selector.select_tables(query, combined_results, max_tables=4)
        except ImportError:
            # Fallback to basic selection if simple selector not available
            selected_tables = _basic_table_selection(combined_results)
        
        # Step 3: Filter columns to selected tables only
        selected_columns = [
            col for col in combined_results.get('columns', [])
            if col.get('table') in selected_tables
        ][:8]  # Limit columns
        
        # Step 4: Create simple confidence scores
        table_scores = {}
        for table in selected_tables:
            # Find best score for this table from semantic results
            best_score = 0.0
            for col in combined_results.get('columns', []):
                if col.get('table') == table:
                    best_score = max(best_score, col.get('score', 0))
            for tbl in combined_results.get('tables', []):
                if tbl.get('table') == table:
                    best_score = max(best_score, tbl.get('score', 0))
            table_scores[table] = best_score
        
        # Convert to legacy format for backward compatibility
        column_ranked = {
            "high": [col for col in selected_columns if col.get('score', 0) >= 0.3],
            "medium": [col for col in selected_columns if 0.15 <= col.get('score', 0) < 0.3],
            "low": [col for col in selected_columns if col.get('score', 0) < 0.15],
            "all_filtered": selected_columns
        }
        
        table_ranked = {
            "high": [{"table": table, "confidence": score * 100, "score": score} 
                    for table, score in table_scores.items() if score >= 0.3],
            "medium": [{"table": table, "confidence": score * 100, "score": score} 
                      for table, score in table_scores.items() if 0.15 <= score < 0.3],
            "low": [{"table": table, "confidence": score * 100, "score": score} 
                   for table, score in table_scores.items() if score < 0.15],
            "all_filtered": [{"table": table, "confidence": score * 100, "score": score} 
                           for table, score in table_scores.items()]
        }
        
        # Build analysis data structure
        analysis_data = {
            "query": query,
            "relevant_tables": selected_tables,
            "column_results": column_ranked,
            "table_results": table_ranked,
            "summary": {
                "total_tables_found": len(selected_tables),
                "high_confidence_columns": len(column_ranked["high"]),
                "high_confidence_tables": len(table_ranked["high"]),
                "total_column_matches": len(column_ranked["all_filtered"]),
                "total_table_matches": len(table_ranked["all_filtered"])
            },
            "best_matches": {
                "top_column": column_ranked["high"][0] if column_ranked["high"] else None,
                "top_table": table_ranked["high"][0] if table_ranked["high"] else None
            },
            "success": True,
            "error": None,
            "table_selection_reasoning": f"Simple semantic search selected {len(selected_tables)} relevant tables",
            "column_selection_reasoning": f"Filtered to columns from selected tables",
            "excluded_tables": []
        }
        
        # Generate SQL prompt if tables found
        prompt_string = ""
        if selected_tables:
            try:
                from llm.sql_prompt_generator import SQLPromptGenerator
                generator = SQLPromptGenerator()
                
                # Generate the prompt
                prompt_string = generator.auto_generate_prompt(
                    query, 
                    selected_tables,
                    context="Simple semantic search identified relevant tables"
                )
                
                analysis_data["prompt_generated"] = True
                
            except ImportError as e:
                analysis_data["success"] = False
                analysis_data["error"] = f"Cannot import SQL prompt generator: {e}"
                prompt_string = f"Error: {e}"
        else:
            analysis_data["success"] = False
            analysis_data["error"] = "No relevant tables found for SQL generation"
            prompt_string = "No relevant tables found. Cannot generate SQL prompt."
        
        return (analysis_data, prompt_string)
        
    except Exception as e:
        # Return error data structure
        error_data = {
            "query": query,
            "relevant_tables": [],
            "column_results": {"high": [], "medium": [], "low": [], "all_filtered": []},
            "table_results": {"high": [], "medium": [], "low": [], "all_filtered": []},
            "summary": {"total_tables_found": 0, "high_confidence_columns": 0, "high_confidence_tables": 0, 
                       "total_column_matches": 0, "total_table_matches": 0},
            "best_matches": {"top_column": None, "top_table": None},
            "success": False,
            "error": str(e),
            "prompt_generated": False,
            "table_selection_reasoning": f"Error: {e}",
            "column_selection_reasoning": f"Error: {e}",
            "excluded_tables": []
        }
        return (error_data, f"Error generating SQL prompt: {e}")


def _basic_table_selection(semantic_results: dict, max_tables: int = 4) -> list:
    """
    Basic fallback table selection if SimpleTableSelector is not available.
    """
    from collections import defaultdict
    
    table_scores = defaultdict(float)
    
    # Get scores from columns
    for col in semantic_results.get('columns', []):
        table = col.get('table')
        score = col.get('score', 0)
        if table and score > table_scores[table]:
            table_scores[table] = score
    
    # Get scores from tables
    for tbl in semantic_results.get('tables', []):
        table = tbl.get('table')
        score = tbl.get('score', 0)
        if table and score > table_scores[table]:
            table_scores[table] = score
    
    # Return top tables sorted by score
    sorted_tables = sorted(table_scores.items(), key=lambda x: x[1], reverse=True)
    return [table for table, score in sorted_tables[:max_tables] if score >= 0.15]


def display_analysis_summary(analysis_data: dict):
    """
    Display a formatted summary of the analysis data.
    
    Args:
        analysis_data: The analysis dictionary from generate_sql_prompt_data()
    """
    print(f"\n📊 ANALYSIS SUMMARY for: '{analysis_data['query']}'")
    print("=" * 60)
    
    if not analysis_data["success"]:
        print(f"❌ Error: {analysis_data['error']}")
        return
    
    # Summary statistics
    summary = analysis_data["summary"]
    print(f"🎯 Tables Found: {summary['total_tables_found']}")
    print(f"📋 Column Matches: {summary['total_column_matches']} ({summary['high_confidence_columns']} high-confidence)")
    print(f"📁 Table Matches: {summary['total_table_matches']} ({summary['high_confidence_tables']} high-confidence)")
    
    # Best matches
    best = analysis_data["best_matches"]
    if best["top_column"]:
        col = best["top_column"]
        print(f"🥇 Best Column: {col['table']}.{col['column']} ({col['confidence']:.1f}%)")
    
    if best["top_table"]:
        tbl = best["top_table"] 
        print(f"🏆 Best Table: {tbl['table']} ({tbl['confidence']:.1f}%)")
    
    # Relevant tables
    if analysis_data["relevant_tables"]:
        print(f"📊 Key Tables: {', '.join(analysis_data['relevant_tables'])}")
    
    # High confidence results
    high_cols = analysis_data["column_results"]["high_confidence"]
    if high_cols:
        print(f"\n🎯 High-Confidence Columns:")
        for col in high_cols[:3]:
            print(f"   • {col['table']}.{col['column']} ({col['confidence']:.1f}%)")
    
    high_tbls = analysis_data["table_results"]["high_confidence"] 
    if high_tbls:
        print(f"\n🏆 High-Confidence Tables:")
        for tbl in high_tbls[:3]:
            print(f"   • {tbl['table']} ({tbl['confidence']:.1f}%)")
    
    print(f"\n✅ Prompt Generated: {analysis_data.get('prompt_generated', False)}")


def main_pipeline(
    clean_db: bool = False,
    force_clean: bool = False,
    collection_prefix: str = "schema",
    run_search_demo: bool = True
):
    """
    Run the complete pipeline: clean, embed, store, and search.
    
    Args:
        clean_db: Whether to clean existing ChromaDB
        force_clean: Force clean without confirmation
        collection_prefix: Prefix for collection names
        run_search_demo: Whether to run search demonstration
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        config = get_config()
        
        # Clean ChromaDB if requested
        if clean_db:
            chroma_path = config.get_chroma_path()
            clean_chroma_db(chroma_path, force=force_clean)
        
        # Create embeddings and store
        results = create_embeddings_and_store(
            collection_prefix=collection_prefix,
            clear_existing=True
        )
        
        if results and run_search_demo:
            search_schema_demo(collection_prefix)
        
        print("\n✅ Pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        print(f"❌ Pipeline failed: {e}")
        raise


def search_only(collection_prefix: str = "schema"):
    """Run only the search demo (assumes embeddings already exist)."""
    setup_logging()
    search_schema_demo(collection_prefix)


# Legacy functions for backwards compatibility
def main():
    """Legacy main function - use main_pipeline() instead."""
    print("⚠️  Using legacy main() function. Consider using main_pipeline() instead.")
    main_pipeline(clean_db=True, force_clean=True)


def search_schema():
    """Legacy search function - use search_only() instead."""
    print("⚠️  Using legacy search_schema() function. Consider using search_only() instead.")
    search_only()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SQL Generator Schema Processing")
    parser.add_argument("--mode", choices=["pipeline", "search", "embed", "custom", "sqlprompt", "sqldata", "sqldetail"], default="pipeline",
                       help="Mode to run: pipeline (full), search (only), embed (only), custom (custom query), sqlprompt (generate SQL prompt), sqldata (return structured data), or sqldetail (detailed analysis)")
    parser.add_argument("--clean", action="store_true", 
                       help="Clean existing ChromaDB before processing")
    parser.add_argument("--force", action="store_true",
                       help="Force clean without confirmation")
    parser.add_argument("--prefix", default="schema",
                       help="Collection prefix for ChromaDB collections")
    parser.add_argument("--no-demo", action="store_true",
                       help="Skip search demonstration")
    parser.add_argument("--query", type=str,
                       help="Query for custom, sqlprompt, or sqldata modes")
    
    args = parser.parse_args()
    
    try:
        if args.mode == "pipeline":
            main_pipeline(
                clean_db=args.clean,
                force_clean=args.force,
                collection_prefix=args.prefix,
                run_search_demo=not args.no_demo
            )
        elif args.mode == "search":
            search_only(args.prefix)
        elif args.mode == "embed":
            create_embeddings_and_store(
                collection_prefix=args.prefix,
                clear_existing=args.clean
            )
        elif args.mode == "custom":
            if args.query:
                custom_search_demo(args.query, args.prefix)
            else:
                # Default query if none provided
                custom_search_demo("how many employees do we have hired before Dec 2023", args.prefix)
        elif args.mode == "sqlprompt":
            if args.query:
                generate_sql_prompt_demo(args.query, args.prefix)
            else:
                # Default query if none provided
                generate_sql_prompt_demo("products never ordered", args.prefix)
        elif args.mode == "sqldata":
            query = args.query if args.query else "products never ordered"
            analysis_data, prompt_string = generate_sql_prompt_data(query, args.prefix)
            
            # Display the analysis summary
            display_analysis_summary(analysis_data)
            
            # Show prompt length and first few lines
            print(f"\n📋 GENERATED PROMPT ({len(prompt_string)} characters):")
            print("-" * 40)
            prompt_lines = prompt_string.split('\n')
            for line in prompt_lines[:10]:
                print(line)
            if len(prompt_lines) > 10:
                print(f"... ({len(prompt_lines)-10} more lines)")
            print("-" * 40)
            
            # Show how to access the data programmatically
            print(f"\n💻 PROGRAMMATIC ACCESS:")
            print("   analysis_data, prompt_string = generate_sql_prompt_data(query)")
            print(f"   analysis_data['summary']['total_tables_found'] = {analysis_data['summary']['total_tables_found']}")
            print(f"   len(prompt_string) = {len(prompt_string)}")
            
        elif args.mode == "sqldetail":
            query = args.query if args.query else "products never ordered"
            analysis_data, prompt_string = generate_sql_prompt_data(query, args.prefix)
            
            # DETAILED ANALYSIS DISPLAY
            print(f"\n🔍 DETAILED SQL ANALYSIS")
            print("=" * 80)
            print(f"📝 Query: '{query}'")
            print("=" * 80)
            
            # Overview
            print(f"\n📊 OVERVIEW")
            print("-" * 40)
            print(f"✅ Success: {analysis_data['success']}")
            print(f"📏 Prompt Length: {len(prompt_string)} characters")
            print(f"📋 Prompt Lines: {len(prompt_string.split(chr(10)))}")
            print(f"🎯 Tables Found: {len(analysis_data['relevant_tables'])}")
            print(f"📊 Relevant Tables: {', '.join(analysis_data['relevant_tables'])}")
            
            # Summary Statistics
            summary = analysis_data['summary']
            print(f"\n📈 SEARCH STATISTICS")
            print("-" * 40)
            print(f"📋 Total Column Matches: {summary['total_column_matches']}")
            print(f"   🎯 High Confidence: {summary['high_confidence_columns']}")
            print(f"📁 Total Table Matches: {summary['total_table_matches']}")
            print(f"   🎯 High Confidence: {summary['high_confidence_tables']}")
            
            # Best Matches
            best = analysis_data['best_matches']
            print(f"\n🏆 BEST MATCHES")
            print("-" * 40)
            if best['top_column']:
                col = best['top_column']
                print(f"🥇 Best Column: {col['table']}.{col['column']}")
                print(f"   📊 Confidence: {col['confidence']:.1f}%")
                print(f"   📝 Text: {col.get('text', 'N/A')[:150]}...")
            else:
                print("🥇 Best Column: None found")
                
            if best['top_table']:
                tbl = best['top_table']
                print(f"🏆 Best Table: {tbl['table']}")
                print(f"   📊 Confidence: {tbl['confidence']:.1f}%")
                print(f"   📝 Text: {tbl.get('text', 'N/A')[:150]}...")
            else:
                print("🏆 Best Table: None found")
            
            # Detailed Column Analysis
            col_results = analysis_data['column_results']
            print(f"\n📋 DETAILED COLUMN ANALYSIS")
            print("-" * 40)
            
            if col_results['high_confidence']:
                print(f"🎯 HIGH CONFIDENCE COLUMNS ({len(col_results['high_confidence'])}):")
                for i, col in enumerate(col_results['high_confidence'], 1):
                    print(f"  {i}. {col['table']}.{col['column']} ({col['confidence']:.1f}%)")
                    print(f"     📝 {col.get('text', 'N/A')[:120]}...")
                    print()
            
            if col_results['medium_confidence']:
                print(f"🔍 MEDIUM CONFIDENCE COLUMNS ({len(col_results['medium_confidence'])}):")
                for i, col in enumerate(col_results['medium_confidence'], 1):
                    print(f"  {i}. {col['table']}.{col['column']} ({col['confidence']:.1f}%)")
                    print(f"     📝 {col.get('text', 'N/A')[:120]}...")
                    print()
            
            # Detailed Table Analysis
            tbl_results = analysis_data['table_results']
            print(f"\n📁 DETAILED TABLE ANALYSIS")
            print("-" * 40)
            
            if tbl_results['high_confidence']:
                print(f"🎯 HIGH CONFIDENCE TABLES ({len(tbl_results['high_confidence'])}):")
                for i, tbl in enumerate(tbl_results['high_confidence'], 1):
                    print(f"  {i}. {tbl['table']} ({tbl['confidence']:.1f}%)")
                    print(f"     📝 {tbl.get('text', 'N/A')[:120]}...")
                    print()
            
            if tbl_results['medium_confidence']:
                print(f"🔍 MEDIUM CONFIDENCE TABLES ({len(tbl_results['medium_confidence'])}):")
                for i, tbl in enumerate(tbl_results['medium_confidence'], 1):
                    print(f"  {i}. {tbl['table']} ({tbl['confidence']:.1f}%)")
                    print(f"     📝 {tbl.get('text', 'N/A')[:120]}...")
                    print()
            
            # SQL Approach Recommendation
            print(f"\n💡 RECOMMENDED SQL APPROACH")
            print("-" * 40)
            relevant_tables = analysis_data['relevant_tables']
            
            if len(relevant_tables) == 1:
                print(f"🎯 Single Table Query:")
                print(f"   • Focus on: {relevant_tables[0]}")
            elif len(relevant_tables) > 1:
                print(f"🔗 Multi-Table Query (JOINs needed):")
                for table in relevant_tables:
                    print(f"   • {table}")
                
                # Simple JOIN suggestions based on common patterns
                print(f"   💡 Common JOIN patterns:")
                if 'cust' in relevant_tables and 'ord_hdr' in relevant_tables:
                    print(f"      - customers ↔ orders (ct_id)")
                if 'ord_hdr' in relevant_tables and 'ord_ln' in relevant_tables:
                    print(f"      - order_header ↔ order_lines (ord_id)")
                if 'ord_ln' in relevant_tables and 'prd_mstr' in relevant_tables:
                    print(f"      - order_lines ↔ products (prd_id)")
                if 'emp_mstr' in relevant_tables:
                    print(f"      - employees table has mgr_id for hierarchies")
            
            # Complete Generated Prompt
            print(f"\n📋 COMPLETE GENERATED PROMPT")
            print("=" * 80)
            print(prompt_string)
            print("=" * 80)
            
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)