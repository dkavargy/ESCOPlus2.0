import json
import networkx as nx
from collections import Counter

# --- SETTINGS ---
target_non_esco_count = 60  # Exactly 60 unique Non-ESCO skills
target_esco_count = 40      # Exactly 40 unique ESCO skills

whitelist = [
    "cloud devops engineer", "security manager", "digital transformation manager",
    "software and applications developers and analysts", "software architect",
    "technical communicator", "electronics engineer", "software developer",
    "mobility services manager"
]

def get_label(item):
    if isinstance(item, str): return item.strip()
    if isinstance(item, dict):
        return item.get('label') or item.get('preferredLabel') or list(item.values())[0]
    return str(item)

# 1. Load Data
file_path = '/content/jobs_experiment_tfidf_all.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

G = nx.Graph()
# Containers to find the most frequent skills globally
global_esco_freq = Counter()
global_non_esco_freq = Counter()
# Container for edge relationships
occ_skill_edges = []

# 2. Extract Data
print("Analyzing dataset for specific skill counts...")
for job in data:
    raw_occs = job.get('mapped_occupations', [])
    valid_occs = [get_label(o).title() for o in raw_occs if get_label(o).lower() in whitelist]

    if not valid_occs:
        continue

    esco_in_job = [get_label(s) for s in job.get('mapped_skills', [])]
    non_esco_in_job = [get_label(s) for s in job.get('non_esco_skills', [])]

    # Update global frequencies
    for s in esco_in_job: global_esco_freq[s] += 1
    for s in non_esco_in_job: global_non_esco_freq[s] += 1

    # Store connections for later
    for occ in valid_occs:
        for s in esco_in_job: occ_skill_edges.append((occ, s, 'ESCO_Skill'))
        for s in non_esco_in_job: occ_skill_edges.append((occ, s, 'Non_ESCO_Skill'))

# 3. Select Top Skills to meet your 60/40 target
top_esco = set([s for s, f in global_esco_freq.most_common(target_esco_count)])
top_non_esco = set([s for s, f in global_non_esco_freq.most_common(target_non_esco_count)])

# 4. Build the Graph
print(f"Building graph with {len(whitelist)} Occupations, {len(top_esco)} ESCO, and {len(top_non_esco)} Non-ESCO...")

# Add Occupations first
for occ in whitelist:
    G.add_node(occ.title(), type='Occupation', label=occ.title())

# Add filtered edges and skill nodes
for occ, skill, s_type in occ_skill_edges:
    if s_type == 'ESCO_Skill' and skill in top_esco:
        G.add_node(skill, type='ESCO_Skill', label=skill)
        G.add_edge(occ, skill)
    elif s_type == 'Non_ESCO_Skill' and skill in top_non_esco:
        G.add_node(skill, type='Non_ESCO_Skill', label=skill)
        G.add_edge(occ, skill)

# 5. Export
nx.write_gml(G, "balanced_60_40_network.gml")
print(f"Done! Created {G.number_of_nodes()} nodes.")
