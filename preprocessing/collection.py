import requests
import json
import urllib3
from time import sleep

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



print("\n==============================")
print("🚀 SKILLAB TRACKER JOB CRAWLER")
print("📌 MODE: KEYWORD-BASED SEARCH")
print("==============================\n")

# ============================================================
# STEP 1: AUTHENTICATION
# ============================================================
def get_token():
    print("🔐 Authenticating...")
    response = requests.post(
        f"{API_BASE_URL}/login",
        json={"username": USERNAME, "password": PASSWORD},
        headers={
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        verify=False
    )

    if response.status_code == 200:
        print("✅ Authentication successful.\n")
        return response.text.replace('"', "")
    else:
        raise RuntimeError(f"❌ Authentication failed: {response.status_code}")

token = get_token()

headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Bearer {token}"
}

# ============================================================
# STEP 2: QUERY CONFIGURATION (KEYWORDS)
# ============================================================
data = {
    "sources": [

    ],
    "keywords": [
        "software engineering",
        "software development",
        "software engineer",
        "backend developer",
        "frontend developer",
        "full stack developer",
        "application developer",
        "systems developer"
    ]
}

print("📌 QUERY CONFIGURATION")
print(f"• Sources ({len(data['sources'])}):")
for src in data["sources"]:
    print(f"  - {src}")

print("\n• Keywords:")
for kw in data["keywords"]:
    print(f"  - {kw}")

# ============================================================
# STEP 3: CRAWL ALL JOB PAGES
# ============================================================
print("\n📥 STARTING JOB CRAWL...\n")

all_results = []
page = 1
total_jobs = 0

while True:
    print(f"➡️  Fetching page {page}...")
    sleep(0.5)

    response = requests.post(
        f"{API_BASE_URL}/jobs?page={page}",
        headers=headers,
        data=data,
        verify=False
    )

    if response.status_code != 200:
        print(f"❌ Error fetching page {page}: {response.status_code}")
        break

    page_data = response.json()
    items = page_data.get("items", [])

    if not items:
        print("🛑 No more pages found. Crawl completed.")
        break

    page_count = len(items)
    total_jobs += page_count

    print(f"   ✔ Retrieved {page_count} jobs (Total: {total_jobs})")

    all_results.extend(items)
    page += 1

print(f"\n✅ TOTAL JOBS COLLECTED: {len(all_results)}")

# ============================================================
# STEP 4: EXTRACT UNIQUE SKILLS & OCCUPATIONS
# ============================================================
print("\n🔎 EXTRACTING UNIQUE SKILLS & OCCUPATIONS...")

unique_skills = set()
unique_occupations = set()

for job in all_results:
    unique_skills.update(job.get("skills", []))
    unique_occupations.update(job.get("occupations", []))

print(f"• Unique skills found: {len(unique_skills)}")
print(f"• Unique occupations found: {len(unique_occupations)}")

# ============================================================
# STEP 5: FETCH LABELS
# ============================================================
def fetch_labels(ids, endpoint, label_type):
    print(f"\n🏷️  Fetching {label_type} labels ({len(ids)} IDs)...")
    results = {}

    for i, id_ in enumerate(ids, start=1):
        try:
            response = requests.post(
                f"{API_BASE_URL}/{endpoint}",
                headers=headers,
                data={"ids": id_},
                verify=False
            )

            if response.status_code == 200:
                label = response.json().get("items", [{}])[0].get("label", "Unknown")
                results[id_] = label
                print(f"   {label_type} {i}/{len(ids)} → {label}")
            else:
                results[id_] = "Unknown"

        except Exception as e:
            print(f"❌ Failed to fetch {label_type} {id_}: {e}")
            results[id_] = "Error"

        sleep(0.1)

    return results

skill_labels = fetch_labels(unique_skills, "skills", "Skill")
occupation_labels = fetch_labels(unique_occupations, "occupations", "Occupation")

# ============================================================
# STEP 6: ENRICH JOB RECORDS
# ============================================================
print("\n🧩 ENRICHING JOB RECORDS...")

for job in all_results:
    job["mapped_skills"] = [
        {"id": s, "label": skill_labels.get(s, "Unknown")}
        for s in job.get("skills", [])
    ]
    job["mapped_occupations"] = [
        {"id": o, "label": occupation_labels.get(o, "Unknown")}
        for o in job.get("occupations", [])
    ]

print("✅ Job enrichment completed.")

# ============================================================
# STEP 7: SAVE OUTPUT
# ============================================================
output_file = "skillab_enriched_jobs_software_keywords.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=4, ensure_ascii=False)

print(f"\n💾 Data saved to: {output_file}")
print("\n🎯 PIPELINE FINISHED SUCCESSFULLY\n")