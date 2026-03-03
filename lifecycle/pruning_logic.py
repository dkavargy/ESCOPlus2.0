import json
import numpy as np
from collections import Counter

whitelist = [
    "cloud devops engineer", "security manager", "digital transformation manager",
    "software and applications developers and analysts", "software architect",
    "technical communicator", "electronics engineer", "software developer",
    "mobility services manager"
]

def get_label(item):
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        return item.get('label') or item.get('preferredLabel') or list(item.values())[0]
    return str(item)

# 1. Load Data
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

occ_to_esco = {}

# 2. Build ESCO Skill Frequency per Occupation
for job in data:
    raw_occs = job.get('mapped_occupations', [])
    valid_occs = [get_label(o).title()
                  for o in raw_occs
                  if get_label(o).lower() in whitelist]

    esco_skills = [get_label(s) for s in job.get('mapped_skills', [])]

    for occ in valid_occs:
        if occ not in occ_to_esco:
            occ_to_esco[occ] = Counter()

        for s in esco_skills:
            occ_to_esco[occ][s] += 1

# 3. Apply Dynamic Pruning Threshold (Q_0.10)
print("\n=== Skills Flagged for Potential Removal (Q_0.10 rule) ===\n")

for occ in occ_to_esco:

    freq_values = list(occ_to_esco[occ].values())

    if len(freq_values) == 0:
        continue

    # Compute 10th percentile
    q_10 = np.percentile(freq_values, 10)

    print(f"\nOccupation: {occ}")
    print(f"Q_0.10 Threshold: {round(q_10, 2)}")
    print("-" * 60)

    flagged_skills = [
        (skill, freq)
        for skill, freq in occ_to_esco[occ].items()
        if freq <= q_10
    ]

    # Sort by frequency ascending
    flagged_skills = sorted(flagged_skills, key=lambda x: x[1])

    for skill, freq in flagged_skills:
        print(f"{skill:45} | f(s) = {freq}")

    print(f"\nTotal flagged skills: {len(flagged_skills)}")

