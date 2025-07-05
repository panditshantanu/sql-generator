#!/usr/bin/env python3
"""
Simple test script for custom search queries
"""

import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from main import custom_search_demo

if __name__ == "__main__":
    # Test your specific query
    query = "how many employees do we have hired before Dec 2023"
    print(f"🔍 Testing query: {query}")
    print("="*80)
    
    try:
        custom_search_demo(query)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nIf you see collection errors, run this first:")
        print("python main.py --mode embed --clean --force")
