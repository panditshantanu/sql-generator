#!/usr/bin/env python3
"""Simple test to verify the enterprise architecture works."""

import sys
sys.path.append('.')

def test_query_analyzer():
    try:
        from sql_generator.core.query_analyzer import QueryAnalyzer
        print('✅ QueryAnalyzer import successful')
        
        qa = QueryAnalyzer()
        print('✅ QueryAnalyzer created successfully')
        print(f'   Confidence threshold: {qa.get_confidence_threshold()}')
        print(f'   Max tables: {qa.get_max_tables()}')
        return True
    except Exception as e:
        print(f'❌ QueryAnalyzer error: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_schema_manager():
    try:
        from sql_generator.core.query_analyzer import QueryAnalyzer
        from sql_generator.core.schema_manager import SchemaManager
        print('✅ SchemaManager import successful')
        
        qa = QueryAnalyzer()
        config = {
            'min_confidence_threshold': 0.5,
            'max_tables_per_query': 5,
            'max_columns_per_table': 3,
            'enable_context_filtering': True
        }
        sm = SchemaManager(qa, config)
        print('✅ SchemaManager created successfully')
        return True
    except Exception as e:
        print(f'❌ SchemaManager error: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    try:
        from sql_generator.main import generate_sql_prompt_data
        print('✅ Integration function import successful')
        
        analysis_data, prompt_string = generate_sql_prompt_data(
            "What products has customer mike purchased?"
        )
        print('✅ Integration test successful')
        print(f'   Success: {analysis_data.get("success", False)}')
        print(f'   Error: {analysis_data.get("error", "None")}')
        print(f'   Tables found: {len(analysis_data.get("relevant_tables", []))}')
        print(f'   Relevant tables: {analysis_data.get("relevant_tables", [])}')
        print(f'   Prompt length: {len(prompt_string)} characters')
        
        # Show first few lines of prompt for debugging
        if prompt_string:
            lines = prompt_string.split('\n')[:5]
            print(f'   Prompt preview: {lines[:2]}...')
        
        return analysis_data.get("success", False)
    except Exception as e:
        print(f'❌ Integration error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Enterprise Architecture Quick Test")
    print("=" * 50)
    
    print("\n1. Testing QueryAnalyzer...")
    test1 = test_query_analyzer()
    
    print("\n2. Testing SchemaManager...")
    test2 = test_schema_manager()
    
    print("\n3. Testing Integration...")
    test3 = test_integration()
    
    print(f"\n📊 Results:")
    print(f"   QueryAnalyzer: {'✅' if test1 else '❌'}")
    print(f"   SchemaManager: {'✅' if test2 else '❌'}")
    print(f"   Integration: {'✅' if test3 else '❌'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 All tests passed! Enterprise architecture is working!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
