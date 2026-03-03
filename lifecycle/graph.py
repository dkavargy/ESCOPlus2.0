import json
import networkx as nx
from collections import Counter

# --- SETTINGS ---
skills_per_category = 10  # 10 ESCO and 10 Non-ESCO per occupation
min_inter_skill_weight = 3 # Minimum co-occurrence to link two different skills

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
occ_to_esco = {}
occ_to_non_esco = {}
skill_co_occurrence = Counter()

# 2. Build Profiles
print("Analyzing occupation and skill relationships...")
for job in data:
    raw_occs = job.get('mapped_occupations', [])
    valid_occs = [get_label(o).title() for o in raw_occs if get_label(o).lower() in whitelist]

    esco_skills = [get_label(s) for s in job.get('mapped_skills', [])]
    non_esco_skills = [get_label(s) for s in job.get('non_esco_skills', [])]

    # Track skill co-occurrence (for ESCO <-> Non-ESCO links)
    all_job_skills = esco_skills + non_esco_skills
    for i in range(len(all_job_skills)):
        for j in range(i + 1, len(all_job_skills)):
            pair = tuple(sorted((all_job_skills[i], all_job_skills[j])))
            skill_co_occurrence[pair] += 1

    for occ in valid_occs:
        if occ not in occ_to_esco:
            occ_to_esco[occ] = Counter()
            occ_to_non_esco[occ] = Counter()
            G.add_node(occ, polygon=0, type='Occupation', label=occ)

        for s in esco_skills: occ_to_esco[occ][s] += 1
        for s in non_esco_skills: occ_to_non_esco[occ][s] += 1

# 3. Add Top 10 + Top 10 Edges
print("Selecting top skills per occupation...")
added_skills = {} # Track skill types for coloring/polygons

for occ in occ_to_esco:
    # Get Top 10 ESCO
    for skill, freq in occ_to_esco[occ].most_common(skills_per_category):
        G.add_node(skill, polygon=1, type='ESCO_Skill', label=skill)
        G.add_edge(occ, skill, weight=freq)
        added_skills[skill] = 1

    # Get Top 10 Non-ESCO
    for skill, freq in occ_to_non_esco[occ].most_common(skills_per_category):
        G.add_node(skill, polygon=2, type='Non_ESCO_Skill', label=skill)
        G.add_edge(occ, skill, weight=freq)
        added_skills[skill] = 2

# 4. Add Inter-Skill Connections (ESCO <-> Non-ESCO)
print("Connecting related skills...")
for (s1, s2), weight in skill_co_occurrence.items():
    # Only link skills that were already added via the Top 10 logic
    if s1 in added_skills and s2 in added_skills and weight >= min_inter_skill_weight:
        # Avoid linking two skills of the same category if you want a cleaner look,
        # or link them all for a dense web.
        if added_skills[s1] != added_skills[s2]:
            G.add_edge(s1, s2, weight=weight, type='skill_link')

# 5. Export
nx.write_gml(G, "balanced_cyber_network.gml")
print(f"Done! Created {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
