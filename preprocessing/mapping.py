import json
import re
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ===============================
# CONFIG
# ===============================
JOB_JSON_PATH = "/content/sample_data/skillab_enriched_jobs_software_keywords.json"
LEXICON_PATH = "/content/sample_data/escoplus_lexicon_not_in_esco.csv"
OUTPUT_PATH = "jobs_experiment_tfidf_all.json"

BATCH_SIZE = 100
NUM_BATCHES = 547             # Increased for TF-IDF as it is much faster
SEMANTIC_THRESHOLD = 0.15    # Note: TF-IDF scores are usually lower than Transformers
MAX_NON_ESCO_SKILLS = 10
NGRAM_RANGE = (1, 2)         # Captures both single words and phrases
MAX_FEATURES = 50000

# ===============================
# NORMALIZATION
# ===============================
def normalize_text(text):
    if not text or not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ===============================
# DATA LOADING
# ===============================
print("Loading lexicon...")
df_lex = pd.read_csv(LEXICON_PATH)
# Normalize and filter short skills
lexicon = df_lex.iloc[:, 0].astype(str).tolist()
lexicon = [normalize_text(s) for s in lexicon if len(s.split()) >= 1]
lexicon = sorted(list(set(lexicon)))
print(f"Loaded {len(lexicon)} unique skills from lexicon")

print("Loading jobs...")
with open(JOB_JSON_PATH, "r", encoding="utf-8") as f:
    jobs = json.load(f)

total_jobs = len(jobs)
max_jobs = min(NUM_BATCHES * BATCH_SIZE, total_jobs)
jobs_subset = jobs[:max_jobs]
print(f"Processing {max_jobs} jobs using TF-IDF strategy")

# ===============================
# TF-IDF VECTORIZATION
# ===============================
print("Preparing corpus and vectorizing...")
# Combine job text (Title + Description)
job_texts = [
    normalize_text(f"{j.get('title','')} {j.get('description','')}")
    for j in jobs_subset
]

# Create global corpus for fitting the vocabulary
full_corpus = job_texts + lexicon

vectorizer = TfidfVectorizer(
    ngram_range=NGRAM_RANGE,
    max_features=MAX_FEATURES,
    stop_words='english' # Optional: helps reduce noise in TF-IDF
)

print("Fitting TF-IDF on corpus...")
vectorizer.fit(full_corpus)

print("Transforming jobs and skills into vectors...")
job_matrix = vectorizer.transform(job_texts)
skill_matrix = vectorizer.transform(lexicon)

# ===============================
# SIMILARITY COMPUTATION
# ===============================
print("Computing similarity matrix...")
# This results in a matrix of shape (num_jobs, num_skills)
sim_matrix = cosine_similarity(job_matrix, skill_matrix)

# ===============================
# MAPPING RESULTS
# ===============================
output_jobs = []

for i, job in enumerate(tqdm(jobs_subset, desc="Mapping Skills")):
    # Get similarity scores for the current job against all skills
    job_scores = sim_matrix[i]

    # Identify indices where score exceeds threshold
    possible_indices = np.where(job_scores >= SEMANTIC_THRESHOLD)[0]

    selected_skills = []
    for idx in possible_indices:
        selected_skills.append({
            "label": lexicon[idx],
            "similarity": round(float(job_scores[idx]), 3),
            "source": "escoplus_tfidf_lexicon"
        })

    # Sort by score descending and limit to MAX_NON_ESCO_SKILLS
    selected_skills = sorted(selected_skills, key=lambda x: x['similarity'], reverse=True)[:MAX_NON_ESCO_SKILLS]

    job["non_esco_skills"] = selected_skills
    output_jobs.append(job)

# ===============================
# SAVE OUTPUT
# ===============================
print(f"Saving results to {OUTPUT_PATH}...")
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output_jobs, f, ensure_ascii=False, indent=2)

print("DONE")