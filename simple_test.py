from sql_generator.main import normalize_score

print("Testing normalize_score function:")
print(f"Score -0.3 -> {normalize_score(-0.3):.1f}%")
print(f"Score 0.0 -> {normalize_score(0.0):.1f}%") 
print(f"Score 0.3 -> {normalize_score(0.3):.1f}%")
print(f"Score 0.8 -> {normalize_score(0.8):.1f}%")
print(f"Score 1.2 -> {normalize_score(1.2):.1f}%")
