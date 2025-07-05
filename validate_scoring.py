"""
Quick validation of the scoring improvements
"""

def test_scoring_improvements():
    print("🔍 Testing Scoring Improvements")
    print("=" * 50)
    
    # Read the current main.py to verify our changes
    with open("sql_generator/main.py", "r") as f:
        content = f.read()
    
    # Check if our changes are in place
    if "min_confidence=50.0" in content:
        print("✅ SQL generation threshold increased to 50%")
    else:
        print("❌ SQL generation threshold not updated")
    
    if "min_confidence=40.0" in content:
        print("✅ Analysis threshold increased to 40%")
    else:
        print("❌ Analysis threshold not updated")
    
    if "column_ranked[\"high\"][:3]" in content:
        print("✅ Column selection limited to high confidence only")
    else:
        print("❌ Column selection still includes medium confidence")
    
    if "table_ranked[\"high\"][:2]" in content:
        print("✅ Table selection limited to high confidence only")
    else:
        print("❌ Table selection still includes medium confidence")
    
    print("\n🎯 Expected Behavior:")
    print("   - Query: 'how many lg products do we have available'")
    print("   - Should ONLY select: prd_mstr table")
    print("   - Should NOT select: cust, ord_ln, wh_mstr, etc.")
    print("   - Higher confidence thresholds should filter out irrelevant tables")

if __name__ == "__main__":
    test_scoring_improvements()
