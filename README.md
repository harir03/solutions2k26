# FairHire — Inspect, Measure, Flag, Fix Bias in Hiring Systems

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-green.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-19-blue.svg)](https://react.dev/)

**FairHire** is a clear, accessible solution to thoroughly inspect datasets and software models for hidden unfairness or discrimination. It provides organizations with an easy way to **measure**, **flag**, and **fix** harmful bias before their systems impact real people.

## 🎯 Problem Statement

Computer programs now make life-changing decisions about who gets a job, a bank loan, or even medical care. However, if these programs learn from flawed or unfair historical data, they will repeat and amplify those exact same discriminatory mistakes.

FairHire addresses this by providing:
- ✅ **Dataset Inspection** — Find bias in your hiring data
- ✅ **Model Auditing** — Prove your model is biased (without accessing proprietary code)
- ✅ **Bias Fixing** — Remove bias and prove it worked

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        FairHire Platform                         │
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │              WEB UI (React + Vite)                      │    │
│   │   Upload │ Dashboard │ Audit View │ Fix View │ Report  │    │
│   └────────────────────────┬───────────────────────────────┘    │
│                            │ REST API                            │
│   ┌────────────────────────┴───────────────────────────────┐    │
│   │              BACKEND (Python + FastAPI)                  │    │
│   │                                                          │    │
│   │   ┌──────────┐   ┌──────────┐   ┌──────────┐           │    │
│   │   │  MODE 1  │   │  MODE 2  │   │  MODE 3  │           │    │
│   │   │ INSPECT  │   │  AUDIT   │   │   FIX    │           │    │
│   │   │ Dataset  │   │  Model   │   │ & Prove  │           │    │
│   │   └────┬─────┘   └────┬─────┘   └────┬─────┘           │    │
│   │        │              │              │                   │    │
│   │   ┌────┴──────────────┴──────────────┴─────┐            │    │
│   │   │         SHARED ENGINES                  │            │    │
│   │   │  ┌─────────────┐  ┌──────────────┐     │            │    │
│   │   │  │  Fairness   │  │  Sequential  │     │            │    │
│   │   │  │  Metrics    │  │  Encoder     │     │            │    │
│   │   │  └─────────────┘  └──────────────┘     │            │    │
│   │   │  ┌─────────────┐  ┌──────────────┐     │            │    │
│   │   │  │  Proxy      │  │  NER Text    │     │            │    │
│   │   │  │  Detector   │  │  Scrubber    │     │            │    │
│   │   │  └─────────────┘  └──────────────┘     │            │    │
│   │   └────────────────────────────────────────┘            │    │
│   │                                                          │    │
│   │   ┌────────────────────────────────────────┐            │    │
│   │   │  LOCAL AI: Gemma 2 2B via Ollama       │            │    │
│   │   │  localhost:11434 (free, offline, fast)  │            │    │
│   │   └────────────────────────────────────────┘            │    │
│   └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Three Core Modes

### Mode 1: INSPECT — "Find the Bias in Your Data"

**What it answers:** *"Is our hiring data fair, or has history baked discrimination into it?"*

#### Input
Upload a CSV with hiring data. Example columns:
```csv
name, gender, age, college, city, skills, experience_years, hired
```

#### Processing Pipeline
1. **Schema Detection** — Auto-detect protected attributes, features, and outcomes
2. **Representation Analysis** — Count distribution per group (flag if any group < 20%)
3. **Label Bias Detection** — Calculate hiring rate per group with statistical significance
4. **Proxy Feature Scanner** — Detect correlations between features and protected attributes
5. **Free-Text PII Scan** — spaCy NER scans for leaked names, locations, organizations
6. **Fairness Scorecard** — Six metrics calculated with pass/fail verdicts

#### Output
- Visual dashboard with 6 metric cards (Red/Yellow/Green)
- Specific evidence for each flag
- Downloadable inspection report

---

### Mode 2: AUDIT — "Prove Your Model Is Biased" ⭐ **HERO FEATURE**

**What it answers:** *"Even if the data looks okay, is the MODEL making unfair decisions?"*

#### Two Sub-Modes
- **2A: Built-in Scorer (Gemma 2 local)** — We provide a resume scorer powered by Gemma 2
- **2B: External Model (Plug any API)** — User provides their company's model endpoint

#### The Differential Testing Engine
1. Select a base resume profile
2. Generate synthetic variants (identical except for names representing different demographics)
3. Send all variants to the model
4. Collect scores and calculate gaps
5. Repeat with 50+ base profiles for statistical significance

#### Why This Beats Existing Tools

| Tool | Requirement | Problem |
|------|-------------|---------|
| IBM AIF360 | Model weights + training data | Companies won't share proprietary info |
| Microsoft Fairlearn | Import model into Python notebook | HR managers don't know Python |
| Google What-If | Manual feature changes | Slow, not automated, not statistical |
| **FairHire** | Just an API endpoint | ✅ Works on ANY system — even human recruiters |

---

### Mode 3: FIX — "Remove the Bias and Prove It Worked"

**What it answers:** *"Okay, bias exists. Now fix it and show me proof."*

#### Three Fix Strategies

1. **Sequential Encoding (Our Innovation)**
   - Every sensitive value → unique sequential code
   - Same value appearing twice → different codes
   - Prevents model from learning patterns like "IIT Bombay = prestigious"

2. **Proxy Removal**
   - Features flagged with correlation > 0.7 are removed entirely
   - Example: "hobbies" column dropped (was 0.87 correlated with gender)

3. **Field Removal**
   - Protected attributes removed or transformed
   - Gender: REMOVED
   - Age: converted to band (20s/30s/40s)
   - Photo, Address: REMOVED (zip code = income proxy)

#### Before/After Proof
```
BEFORE FIXES              AFTER FIXES

Fairness: 42/100 🔴      Fairness: 91/100 🟢
Accuracy: 78/100         Accuracy: 74/100

Gender Gap: 29pts 🔴     Gender Gap: 3pts ✅
Religion Gap: 22pts 🔴   Religion Gap: 2pts ✅
College Gap: 18pts ⚠️    College Gap: 1pt ✅

TRADEOFF VERDICT
Fairness gained: +49 points
Accuracy lost:    -4 points

Recommendation: APPLY FIXES ✅
```

---

## 📊 Six Fairness Metrics

| # | Metric | Formula | Pass Threshold | What It Catches |
|---|--------|---------|----------------|-----------------|
| 1 | Demographic Parity Ratio | (worst group rate) ÷ (best group rate) | ≥ 0.8 | Unequal selection rates |
| 2 | Disparate Impact | Same as DPR — legal name (US 4/5 rule) | ≥ 0.8 | Legal compliance check |
| 3 | Equal Opportunity Difference | TPR(group A) − TPR(group B) | < 0.1 | Equal chances among qualified |
| 4 | Predictive Parity | Precision(A) − Precision(B) | < 0.1 | Equal accuracy across groups |
| 5 | Proxy Leak Score | Max correlation with protected attribute | < 0.6 | Hidden info leakage |
| 6 | Representation Index | Min group % ÷ Expected group % | ≥ 0.5 | Dataset completeness |

---

## 🛡️ Quarantine Gate (Safety Net)

If bias metrics still fail after fixes:

```
┌──────────────────────────────────────────┐
│  ⚠️ QUARANTINE ACTIVE                    │
│                                          │
│  Results held — NOT released to HR       │
│                                          │
│  Reason: Gender gap still 12pts          │
│  (threshold: <5pts)                      │
│                                          │
│  Options:                                │
│  [Apply stronger fixes]                  │
│  [Override with justification]           │
│  [Reject batch]                          │
└──────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Role |
|-----------|------------|------|
| Frontend | React 19 + Vite | Dashboard, charts, upload UI |
| Backend | Python 3.12 + FastAPI | API, data processing, metrics |
| Local AI | Gemma 2 2B via Ollama | Resume scoring (free, offline) |
| Data | Pandas + NumPy | CSV parsing, statistical analysis |
| Metrics | Scikit-learn + custom | Correlation, fairness calculations |
| NER | spaCy (en_core_web_sm) | Free-text PII detection |
| Charts | Recharts | Bar charts, heatmaps, comparisons |
| Reports | html2pdf / jsPDF | Export compliance PDF |
| Storage | In-memory (hackathon) | No database needed for MVP |

### Everything Runs Locally

```
Your laptop:
├── React dev server          → localhost:5173
├── FastAPI backend           → localhost:8000
├── Ollama + Gemma 2 2B      → localhost:11434
└── Zero internet dependency. Zero API costs. Zero rate limits.
```

---

## 📡 API Contracts

### POST /api/upload
```json
// Request: multipart/form-data with CSV file
// Response:
{
  "dataset_id": "d_001",
  "rows": 500,
  "columns": ["name","gender","age","college","city","skills","experience","hired"],
  "detected_protected": ["name","gender","age"],
  "detected_features": ["college","city","skills","experience"],
  "detected_outcome": "hired"
}
```

### POST /api/inspect
```json
// Request:
{ "dataset_id": "d_001" }
// Response:
{
  "fairness_score": 42,
  "representation": {
    "gender": {"Male": 0.78, "Female": 0.22},
    "verdict": "IMBALANCED"
  },
  "label_bias": {
    "Male_hired_rate": 0.67,
    "Female_hired_rate": 0.38,
    "gap": 0.29,
    "severity": "CRITICAL"
  },
  "proxies": [
    {"feature": "hobbies", "proxy_for": "gender", "correlation": 0.87, "action": "REMOVE"},
    {"feature": "college", "proxy_for": "hired", "correlation": 0.72, "action": "WARN"}
  ],
  "metrics": {
    "demographic_parity_ratio": 0.57,
    "disparate_impact": 0.57,
    "equal_opportunity_diff": 0.24,
    "predictive_parity_diff": 0.18,
    "proxy_leak_score": 0.87,
    "representation_index": 0.28
  }
}
```

### POST /api/audit
```json
// Request:
{
  "dataset_id": "d_001",
  "model": "builtin",
  "external_url": null,
  "num_base_profiles": 50,
  "name_variants": ["Rahul Sharma","Priya Patel","Mohammed Khan","Fatima Begum","John Smith"]
}
// Response:
{
  "total_tests": 250,
  "bias_detected": true,
  "gaps": [
    {"attribute": "gender", "gap": 15.2, "favored": "male", "severity": "HIGH", "p_value": 0.0003},
    {"attribute": "religion", "gap": 22.1, "favored": "hindu_name", "severity": "CRITICAL", "p_value": 0.0001}
  ]
}
```

---

## 🎯 Key Differentiators

- **No-Code Web UI** — Upload CSV, click buttons, read visual dashboard. No Python needed
- **Black-Box Testing** — Audit any model without accessing source code or weights
- **Before/After Proof** — Quantifiable evidence that fixes work
- **Quarantine System** — Biased results are HELD until human review
- **100% Local** — No cloud dependencies, no API costs, complete privacy

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

We welcome contributions! Please read our contributing guidelines before submitting PRs.

---

**Built with ❤️ to make AI fair for everyone.**
