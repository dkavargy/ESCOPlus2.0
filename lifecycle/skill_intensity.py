with open(file_path, 'r', encoding='utf-8') as f:
    jobs = json.load(f)

total_jobs = len(jobs)

def get_frequencies(category_key):
    counts = Counter()
    for job in jobs:
        items = job.get(category_key, [])
        # Use set to count only once per document (o_ij is number of documents)
        unique_labels = {item.get('label') for item in items if item.get('label')}
        for label in unique_labels:
            counts[label] += 1

    # Calculate o_ij / n_j
    freq_data = []
    for label, count in counts.items():
        freq_data.append({
            'label': label,
            'count': count,
            'frequency': count / total_jobs
        })

    # Sort and take top 50
    df = pd.DataFrame(freq_data)
    if not df.empty:
        df = df.sort_values(by='frequency', ascending=False).head(100)
    return df

# Process categories
top_mapped_skills = get_frequencies('mapped_skills')
top_mapped_occupations = get_frequencies('mapped_occupations')
top_non_esco_skills = get_frequencies('non_esco_skills')

# Save to CSV for the user
top_mapped_skills.to_csv('top_mapped_skills.csv', index=False)
top_mapped_occupations.to_csv('top_mapped_occupations.csv', index=False)
top_non_esco_skills.to_csv('top_non_esco_skills.csv', index=False)

# Print summaries
print(f"Total jobs (nj): {total_jobs}")
print("\n--- Top 10 Mapped Skills ---")
print(top_mapped_skills.head(100))
print("\n--- Top 10 Mapped Occupations ---")
print(top_mapped_occupations.head(100))
print("\n--- Top 10 Non-ESCO Skills ---")
print(top_non_esco_skills.head(180))

top_mapped_skills.to_csv('top_mapped_skills.csv', index=False)
top_mapped_occupations.to_csv('top_mapped_occupations.csv', index=False)
top_non_esco_skills.to_csv('top_non_esco_skills.csv', index=False)

with open(file_path, 'r', encoding='utf-8') as f:
    jobs = json.load(f)

total_jobs = len(jobs)

def get_frequencies(category_key):
    counts = Counter()
    total_mentions = 0  # Total count of all items found

    for job in jobs:
        items = job.get(category_key, [])
        total_mentions += len(items)

        # Use set to count only once per document (o_ij is number of documents)
        unique_labels = {item.get('label') for item in items if item.get('label')}
        for label in unique_labels:
            counts[label] += 1

    # Calculate o_ij / n_j
    freq_data = []
    for label, count in counts.items():
        freq_data.append({
            'label': label,
            'count': count,
            'frequency': count / total_jobs
        })

    df = pd.DataFrame(freq_data)
    if not df.empty:
        df = df.sort_values(by='frequency', ascending=False)

    return df, len(counts), total_mentions

# Process categories and get totals
top_mapped_skills, unique_skills_count, total_skills_mentions = get_frequencies('mapped_skills')
top_mapped_occupations, unique_occs_count, total_occs_mentions = get_frequencies('mapped_occupations')
top_non_esco_skills, unique_non_esco_count, total_non_esco_mentions = get_frequencies('non_esco_skills')

# Save Top 50 to CSV for the user
top_mapped_skills.head(50).to_csv('top_mapped_skills.csv', index=False)
top_mapped_occupations.head(50).to_csv('top_mapped_occupations.csv', index=False)
top_non_esco_skills.head(50).to_csv('top_non_esco_skills.csv', index=False)

# --- MARKET DIVERSITY SUMMARY ---
print(f"Total jobs analyzed (n_j): {total_jobs}")
print("-" * 40)

summary_data = {
    "Category": ["Mapped ESCO Skills", "Mapped Occupations", "Non-ESCO Skills"],
    "Unique Entities (Diversity)": [unique_skills_count, unique_occs_count, unique_non_esco_count],
    "Total Mentions (Density)": [total_skills_mentions, total_occs_mentions, total_non_esco_mentions],
    "Avg per Job": [total_skills_mentions/total_jobs, total_occs_mentions/total_jobs, total_non_esco_mentions/total_jobs]
}

summary_df = pd.DataFrame(summary_data)
print(summary_df.to_string(index=False))

print("\n--- Detailed Top 10 Lists ---")
print("\nMapped Skills:\n", top_mapped_skills.head(10))
print("\nMapped Occupations:\n", top_mapped_occupations.head(10))
print("\nNon-ESCO Skills:\n", top_non_esco_skills.head(10))

def coverage_rate(category_key):
    jobs_with_skill = 0

    for job in jobs:
        items = job.get(category_key, [])
        if items and len(items) > 0:
            jobs_with_skill += 1

    return jobs_with_skill, jobs_with_skill / total_jobs

coverage_skills = coverage_rate('mapped_skills')
coverage_occs = coverage_rate('mapped_occupations')
coverage_non_esco = coverage_rate('non_esco_skills')

print("\n--- Coverage Rates ---")
print(f"ESCO Skills Coverage: {coverage_skills[0]} jobs ({coverage_skills[1]:.2%})")
print(f"Occupations Coverage: {coverage_occs[0]} jobs ({coverage_occs[1]:.2%})")
print(f"Non-ESCO Skills Coverage: {coverage_non_esco[0]} jobs ({coverage_non_esco[1]:.2%})")

import numpy as np

def per_job_distribution(category_key):
    counts = [len(job.get(category_key, [])) for job in jobs]

    return {
        "mean": np.mean(counts),
        "median": np.median(counts),
        "std": np.std(counts),
        "min": np.min(counts),
        "max": np.max(counts)
    }

print("\n--- Per Job Distribution ---")
print("ESCO Skills:", per_job_distribution('mapped_skills'))
print("Non-ESCO Skills:", per_job_distribution('non_esco_skills'))
print("Occupations:", per_job_distribution('mapped_occupations'))
