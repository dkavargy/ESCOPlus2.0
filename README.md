[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Status](https://img.shields.io/badge/Status-Research--Prototype-orange)

# ESCOPlus 2.0: Dynamic Taxonomy Extension and Pruning Framework

**ESCOPlus 2.0** is an open-source research framework designed to systematically extend, validate, and refine the ESCO skills taxonomy using real Online Job Advertisement (OJA) data across Europe.

Unlike static taxonomy alignment tools, ESCOPlus 2.0 introduces a lifecycle-driven maintenance logic grounded in quantitative labor market demand.

---

## 📌 Project Overview

Occupational taxonomies such as ESCO must continuously evolve to remain aligned with emerging technologies and changing labor market needs.

ESCOPlus 2.0 provides:

- Demand-driven skill extension
- Quantitative pruning logic
- Occupation–skill bipartite modeling
- Statistical governance via structured agreement protocols
- Web-based operationalization (SKILLAB platform integration)

The framework bridges:

- Real-time EU Online Job Advertisements
- ESCO skill and occupation mappings
- Non-ESCO skill discovery
- Lifecycle-based decision thresholds

---

## 🧠 Conceptual Architecture

ESCOPlus 2.0 operates in four core layers:

### 1️⃣ Data Acquisition Layer
- EU Online Job Advertisements (JSON format)
- ISCO-based occupation classification

### 2️⃣ Extraction & Matching Layer
- ESCO skill detection
- Non-ESCO skill discovery (TF-IDF / semantic similarity)
- Occupation–skill intensity calculation

### 3️⃣ Lifecycle Evaluation Layer
- Skill Intensity Indicator  
  \( SI_{s,j} = \frac{o_{ij}}{n_j} \)
- Growth threshold (e.g., Q90 percentile logic)
- Emerging vs declining skill detection

### 4️⃣ Governance & Validation Layer
- Bipartite occupation–skill graph modeling
- Inter-rater agreement computation
- Structured voting protocol
- Sensitivity analysis for threshold robustness

---

## 📊 Skill Intensity Indicator

The core indicator used in ESCOPlus 2.0:

\[
SI_{s,j} = \frac{o_{ij}}{n_j}
\]

Where:

- \( o_{ij} \): number of job ads for occupation \( j \) mentioning skill \( s \)
- \( n_j \): total job ads for occupation \( j \)

Extension rule:

A non-ESCO skill \( s \in S_{\text{non-ESCO}} \) is flagged for inclusion if:

\[
SI_{s,j} \geq Q_{0.90}
\]

Only the top 10% most demanded candidate skills are retained.

Pruning rule:

ESCO skills with persistently low occupational intensity are flagged for review.

---

## 🔄 Cloning This Repository

To clone this repository and all submodules:

```bash
git clone --recurse-submodules https://github.com/dkavary/ESCOPlus2.0.git
```

Or:

```bash
git clone https://github.com/dkavargy/ESCOPlus2.0.git
cd ESCOPlus2.0
git submodule update --init --recursive
```

---

## 🧪 Core Features

- 📊 Large-scale OJA processing
- 🔍 ESCO + Non-ESCO skill detection
- 📈 Occupation-specific Skill Intensity computation
- 🧮 Percentile-based extension thresholds (Q90 logic)
- 🗑️ Low-demand pruning mechanism
- 🗳️ Structured consensus-based validation
- 🌐 Web-based governance dashboard integration

---

## 🖥️ Web Interface

ESCOPlus 2.0 is operationalized through a web-based platform integrated within the SKILLAB project infrastructure.

The platform enables:

- Interactive occupation–skill exploration
- Emerging skill detection
- Pruning candidate visualization
- Taxonomy export functionality

---

## 📁 Project Structure

```bash
ESCOPlus2.0/
├── README.md
├── LICENSE
├── requirements.txt
├── data/
│   ├── raw/                  # Online Job Advertisements (JSON)
│   ├── processed/            # Extracted skills and occupation mappings
│   └── taxonomy_snapshots/   # ESCO versions and updates
├── notebooks/                # Experimental and validation notebooks
├── src/
│   ├── extraction/
│   │   ├── esco_matching.py
│   │   ├── non_esco_detection.py
│   │   └── tfidf_pipeline.py
│   ├── metrics/
│   │   ├── skill_intensity.py
│   │   ├── lifecycle_analysis.py
│   │   └── thresholding.py
│   ├── graph/
│   │   ├── bipartite_builder.py
│   │   └── network_analysis.py
│   ├── evaluation/
│   │   ├── agreement.py
│   │   ├── voting_protocol.py
│   │   └── validation_metrics.py
│   └── utils/
│       └── preprocessing.py
├── dashboard/
│   ├── app.py
│   └── components/
└── experiments/
    ├── threshold_sensitivity/
    └── performance_tests/
```

---

## 🔬 Scientific Foundations

ESCOPlus 2.0 builds upon:

- Taxonomy enrichment frameworks (NEO, WETA, MEET-LM)
- Skill lifecycle modeling logic
- Statistical governance methodologies
- Large-scale labor market intelligence

---

## 🎯 Research Questions

1. Which skills are strongly demanded in EU software occupations?
2. Which non-ESCO skills should be integrated?
3. Which ESCO skills show persistent decline?
4. How can stakeholders operationalize taxonomy updates in real time?

---

## 🧩 Difference from ESCOPlus 1.0

| ESCOPlus 1.0 | ESCOPlus 2.0 |
|--------------|--------------|
| Supply-driven (Stack Overflow) | Demand-driven (OJAs) |
| Skill discovery only | Discovery + pruning |
| Static analysis | Lifecycle logic |
| No structured governance | Statistical consensus protocol |

---

## 📜 License

This project is licensed under the MIT License.
