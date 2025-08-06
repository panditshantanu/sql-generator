"""
LLM Setup and Testing Script for SQL Generator.
Helps configure and test LLM integrations.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from sql_generator.llm.llm_service import LLMService, create_llm_service
    from sql_generator.llm.sql_prompt_generator import SQLPromptGenerator
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(current_dir / "sql_generator"))
    from llm.llm_service import LLMService, create_llm_service
    from llm.sql_prompt_generator import SQLPromptGenerator


def setup_environment_variables():
    """Guide user through setting up environment variables."""
    print("🔧 LLM ENVIRONMENT SETUP")
    print("=" * 50)
    
    # Check current environment
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print(f"Current Status:")
    print(f"  OpenAI API Key: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"  Anthropic API Key: {'✅ Set' if anthropic_key else '❌ Not set'}")
    
    if not openai_key and not anthropic_key:
        print(f"\n⚠️  No API keys found!")
        print(f"\nTo set up LLM integration:")
        print(f"1. For OpenAI (recommended):")
        print(f"   - Get API key from: https://platform.openai.com/api-keys")
        print(f"   - Set environment variable: OPENAI_API_KEY=your_key_here")
        print(f"   - Windows: set OPENAI_API_KEY=your_key_here")
        print(f"   - Linux/Mac: export OPENAI_API_KEY=your_key_here")
        print(f"\n2. For Anthropic:")
        print(f"   - Get API key from: https://console.anthropic.com/")
        print(f"   - Set environment variable: ANTHROPIC_API_KEY=your_key_here")
        print(f"\n3. For Local LLM (Ollama):")
        print(f"   - Install Ollama: https://ollama.ai/")
        print(f"   - Pull a code model: ollama pull codellama:7b")
        print(f"   - Start Ollama service")
        
        return False
    
    return True


def test_llm_providers():
    """Test available LLM providers."""
    print("\n🧪 TESTING LLM PROVIDERS")
    print("=" * 50)
    
    try:
        service = create_llm_service()
        health = service.health_check()
        
        if not health:
            print("❌ No providers available")
            return False
        
        print("Provider Status:")
        for provider, status in health.items():
            status_icon = "✅" if status else "❌"
            print(f"  {provider}: {status_icon}")
        
        # Test with a simple prompt
        test_prompt = """You are an expert SQL generator. Generate a simple SQL query.

Database Schema:
Table: users
  Columns:
    - id: INTEGER NOT NULL - User ID
    - name: VARCHAR(100) NOT NULL - User name
    - email: VARCHAR(255) NOT NULL - User email

User Question: "Get all users"

Instructions:
- Generate only the SQL query, no explanations

SQL Query:"""
        
        print(f"\n🔬 Testing SQL generation...")
        available_providers = [p for p, status in health.items() if status]
        
        if available_providers:
            test_provider = available_providers[0]
            print(f"Testing with: {test_provider}")
            
            response = service.generate_sql(test_prompt, preferred_provider=test_provider)
            
            if response.success:
                print(f"✅ Test successful!")
                print(f"Generated SQL: {response.sql_query}")
                print(f"Provider: {response.provider}")
                print(f"Model: {response.model}")
                if response.response_time:
                    print(f"Response time: {response.response_time:.2f}s")
                return True
            else:
                print(f"❌ Test failed: {response.error}")
                return False
        else:
            print(f"❌ No providers available for testing")
            return False
            
    except Exception as e:
        print(f"❌ Error testing providers: {e}")
        return False


def interactive_sql_generation():
    """Interactive SQL generation demo."""
    print("\n🎯 INTERACTIVE SQL GENERATION")
    print("=" * 50)
    
    try:
        # Initialize components
        generator = SQLPromptGenerator(enable_llm=True)
        
        if not generator.enable_llm:
            print("❌ LLM integration not available")
            return
        
        print("Enter your natural language queries (type 'quit' to exit):")
        
        while True:
            query = input("\n💬 Your query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
                
            if not query:
                continue
            
            print(f"\n🔍 Processing: '{query}'")
            
            # For demo, use some sample tables
            sample_tables = ["users", "orders", "products"]
            
            try:
                result = generator.generate_sql_with_llm(query, sample_tables)
                
                if result["success"]:
                    print(f"✅ SQL Generated:")
                    print(f"Provider: {result['provider']}")
                    print(f"SQL Query:")
                    print("-" * 40)
                    print(result["sql_query"])
                    print("-" * 40)
                else:
                    print(f"❌ Failed: {result['error']}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Setup error: {e}")


def install_dependencies():
    """Guide user through installing LLM dependencies."""
    print("\n📦 DEPENDENCY INSTALLATION")
    print("=" * 50)
    
    print("Required packages for LLM integration:")
    print("1. OpenAI: pip install openai")
    print("2. Anthropic: pip install anthropic")
    print("3. Requests (for local LLM): pip install requests")
    
    try:
        import openai
        print("✅ OpenAI package installed")
    except ImportError:
        print("❌ OpenAI package not installed")
        print("   Install with: pip install openai")
    
    try:
        import anthropic
        print("✅ Anthropic package installed")
    except ImportError:
        print("❌ Anthropic package not installed")
        print("   Install with: pip install anthropic")
    
    try:
        import requests
        print("✅ Requests package installed")
    except ImportError:
        print("❌ Requests package not installed")
        print("   Install with: pip install requests")


def main():
    """Main setup function."""
    print("🚀 SQL GENERATOR LLM SETUP")
    print("=" * 60)
    
    # Check dependencies
    install_dependencies()
    
    # Setup environment
    if setup_environment_variables():
        # Test providers
        if test_llm_providers():
            # Interactive demo
            response = input("\n🎮 Run interactive SQL generation demo? (y/N): ")
            if response.lower() == 'y':
                interactive_sql_generation()
        else:
            print("\n⚠️  Provider testing failed. Check your configuration.")
    else:
        print("\n⚠️  Please set up API keys first.")
    
    print(f"\n✅ Setup complete!")
    print(f"Next steps:")
    print(f"1. Set your API keys as environment variables")
    print(f"2. Run: python main.py --mode sqlgen --query 'your question'")
    print(f"3. Or use the interactive mode with run_sql_generator.py")


if __name__ == "__main__":
    main()
