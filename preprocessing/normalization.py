# import json

# with open('/content/jobs_experiment_tfidf_all.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)

# print(f"Total jobs in file: {len(data)}")

import json
from collections import Counter

# 1. Load the data
file_path = '/content/jobs_experiment_tfidf_all.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def explore_structure(obj, indent=0, max_depth=3):
    """Recursively prints the structure (keys and types) of the JSON."""
    spacing = "  " * indent
    if indent > max_depth:
        return

    if isinstance(obj, dict):
        print(f"{spacing}{{Dict with {len(obj)} keys}}")
        for key, value in list(obj.items())[:16]: # Show first 5 keys
            print(f"{spacing}  - {key}: {type(value).__name__}")
            if isinstance(value, (dict, list)):
                explore_structure(value, indent + 2, max_depth)
        if len(obj) > 5:
            print(f"{spacing}  ... ({len(obj)-5} more keys)")

    elif isinstance(obj, list):
        print(f"{spacing}[List with {len(obj)} items]")
        if len(obj) > 0:
            print(f"{spacing}  Sample Item Structure:")
            explore_structure(obj[0], indent + 2, max_depth)

            # Clever check: If it's a list of dicts, what are the most common keys?
            if isinstance(obj[0], dict):
                all_keys = [k for d in obj if isinstance(d, dict) for k in d.keys()]
                print(f"{spacing}  Key Frequency: {dict(Counter(all_keys).most_common(5))}")

print(f"File: {file_path}")
print("-" * 30)
explore_structure(data)