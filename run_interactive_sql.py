#!/usr/bin/env python3
"""
Interactive SQL Generator - Enhanced with LLM Integration
Production-ready SQL generation from natural language queries.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from sql_generator.main import (
        generate_sql_prompt_data, 
        generate_sql_with_llm,
        custom_search_demo
    )
    from sql_generator.llm.llm_service import create_llm_service
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def print_header():
    """Print application header."""
    print("=" * 70)
    print("🚀 SQL GENERATOR - AI-Powered Database Query Generation")
    print("=" * 70)
    print("Features:")
    print("  • Semantic schema search")
    print("  • Intelligent table selection") 
    print("  • Multi-provider LLM integration")
    print("  • Production-ready SQL generation")
    print("=" * 70)


def check_llm_status():
    """Check and display LLM provider status."""
    try:
        service = create_llm_service()
        health = service.health_check()
        available_providers = [p for p, status in health.items() if status]
        
        print(f"\n🤖 LLM PROVIDER STATUS:")
        for provider, status in health.items():
            icon = "✅" if status else "❌"
            print(f"  {provider}: {icon}")
        
        if available_providers:
            print(f"✅ Ready with {len(available_providers)} provider(s)")
            return True
        else:
            print(f"⚠️  No LLM providers available")
            print(f"   Run 'python setup_llm.py' to configure")
            return False
            
    except Exception as e:
        print(f"❌ LLM service error: {e}")
        return False


def interactive_mode():
    """Run interactive SQL generation."""
    print(f"\n🎯 INTERACTIVE SQL GENERATION")
    print("Commands:")
    print("  • Enter natural language queries")
    print("  • Type 'demo' for schema search demo")
    print("  • Type 'prompt' for prompt-only mode")
    print("  • Type 'help' for assistance")
    print("  • Type 'quit' to exit")
    print("-" * 50)
    
    llm_available = check_llm_status()
    
    while True:
        try:
            query = input("\n💬 Your query: ").strip()
            
            if not query:
                continue
                
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            elif query.lower() == 'help':
                show_help()
                continue
                
            elif query.lower() == 'demo':
                print("\n🔍 Running schema search demo...")
                custom_search_demo("find customer orders with products")
                continue
                
            elif query.lower() == 'prompt':
                print("\n📝 Prompt-only mode:")
                prompt_mode(query)
                continue
            
            # Main SQL generation
            print(f"\n🔍 Processing: '{query}'")
            
            if llm_available:
                # Full LLM integration
                result = generate_sql_with_llm(query)
                display_sql_result(result)
            else:
                # Fallback to prompt generation only
                print("⚠️  LLM not available, generating prompt only...")
                analysis_data, prompt = generate_sql_prompt_data(query)
                display_prompt_result(analysis_data, prompt)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def prompt_mode(initial_query=None):
    """Prompt-only generation mode."""
    while True:
        if initial_query:
            query = initial_query
            initial_query = None  # Only use once
        else:
            query = input("\n💬 Query for prompt: ").strip()
            
        if query.lower() in ['quit', 'exit', 'back']:
            break
            
        if query:
            print(f"\n📝 Generating prompt for: '{query}'")
            analysis_data, prompt = generate_sql_prompt_data(query)
            display_prompt_result(analysis_data, prompt)


def display_sql_result(result):
    """Display SQL generation result."""
    if result["success"]:
        print(f"\n✅ SQL GENERATED SUCCESSFULLY")
        print("-" * 40)
        print(f"🤖 Provider: {result.get('provider', 'unknown')}")
        print(f"📊 Model: {result.get('model', 'unknown')}")
        print(f"⏱️ Time: {result.get('response_time', 0):.2f}s")
        print(f"🎯 Tables: {', '.join(result.get('selected_tables', []))}")
        
        print(f"\n📋 SQL QUERY:")
        print("=" * 50)
        print(result["sql_query"])
        print("=" * 50)
        
        # Analysis details
        analysis = result.get("analysis", {})
        semantic = result.get("semantic_results", {})
        
        print(f"\n📊 ANALYSIS:")
        print(f"  Query Type: {analysis.get('query_type', 'unknown')}")
        print(f"  Complexity: {analysis.get('complexity', 'unknown')}")
        print(f"  Tables Found: {semantic.get('total_tables_found', 0)}")
        print(f"  Columns Found: {semantic.get('total_columns_found', 0)}")
        
        if result.get('tokens_used'):
            print(f"  Tokens Used: {result['tokens_used']}")
            
    else:
        print(f"\n❌ SQL GENERATION FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")
        
        # Show what was attempted
        if result.get("selected_tables"):
            print(f"Tables identified: {', '.join(result['selected_tables'])}")


def display_prompt_result(analysis_data, prompt):
    """Display prompt generation result."""
    if analysis_data["success"]:
        print(f"\n✅ PROMPT GENERATED")
        print("-" * 40)
        
        summary = analysis_data["summary"]
        print(f"🎯 Tables: {summary['total_tables_found']}")
        print(f"📋 Columns: {summary['total_column_matches']}")
        print(f"🏆 High Confidence: {summary['high_confidence_columns']} cols, {summary['high_confidence_tables']} tables")
        
        print(f"\n📋 GENERATED PROMPT:")
        print("=" * 50)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("=" * 50)
        
        print(f"\n💡 USAGE:")
        print("  1. Copy the prompt above")
        print("  2. Send to ChatGPT, Claude, or your LLM")
        print("  3. Get your SQL query!")
        
    else:
        print(f"\n❌ PROMPT GENERATION FAILED")
        print(f"Error: {analysis_data.get('error', 'Unknown error')}")


def show_help():
    """Show help information."""
    print(f"\n📚 HELP & EXAMPLES")
    print("-" * 40)
    print("Example queries:")
    print("  • 'how many customers do we have?'")
    print("  • 'list all products never ordered'")
    print("  • 'top 10 customers by total orders'")
    print("  • 'employees hired in the last 6 months'")
    print("  • 'average order value by month'")
    
    print(f"\nTips for better results:")
    print("  • Be specific about what you want")
    print("  • Mention timeframes if relevant")
    print("  • Use business terms (customers, orders, products)")
    print("  • Ask for specific metrics (count, sum, average)")


def main():
    """Main entry point."""
    print_header()
    
    try:
        # Check if we have a query from command line
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])
            print(f"\n🔍 Processing command line query: '{query}'")
            
            llm_available = check_llm_status()
            
            if llm_available:
                result = generate_sql_with_llm(query)
                display_sql_result(result)
            else:
                analysis_data, prompt = generate_sql_prompt_data(query)
                display_prompt_result(analysis_data, prompt)
        else:
            # Interactive mode
            interactive_mode()
            
    except Exception as e:
        print(f"❌ Application error: {e}")
        print("Please check your configuration and try again")


if __name__ == "__main__":
    main()
